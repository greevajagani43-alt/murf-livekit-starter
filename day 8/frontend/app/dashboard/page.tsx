"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { Room, RoomEvent, Track } from "livekit-client";

interface DashboardStats {
  totalCalls: number;
  successfulCalls: number;
  failedCalls: number;
}

interface CallRecord {
  id: number;
  call_id: string;
  masked_call_id: string;
  call_type: string;
  started_at: string;
  ended_at: string | null;
  duration: number;
  outcome: string;
  reason: string;
  created_at: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({ totalCalls: 0, successfulCalls: 0, failedCalls: 0 });
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState("");

  // Live call (mini caller panel)
  const [isCalling, setIsCalling] = useState(false);
  const [callStatus, setCallStatus] = useState("Idle");
  const roomRef = useRef<Room | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [sRes, cRes] = await Promise.all([
        fetch("/api/dashboard/stats", { cache: "no-store" }),
        fetch("/api/calls", { cache: "no-store" }),
      ]);
      if (sRes.ok) {
        const d = await sRes.json();
        setStats({ totalCalls: d.totalCalls ?? 0, successfulCalls: d.successfulCalls ?? 0, failedCalls: d.failedCalls ?? 0 });
      }
      if (cRes.ok) {
        const d = await cRes.json();
        if (Array.isArray(d)) setCalls(d);
      }
      setLastUpdated(new Date().toLocaleTimeString());
    } catch {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetchData();
    const t = setInterval(fetchData, 3000);
    return () => clearInterval(t);
  }, [fetchData]);

  const startTestCall = async () => {
    if (isCalling) return;
    setIsCalling(true);
    setCallStatus("Connecting...");
    try {
      const roomName = `browser_call_${Date.now()}`;
      const res = await fetch(`/api/token?roomName=${roomName}`);
      if (!res.ok) throw new Error("Token failed");
      const { token, serverUrl } = await res.json();
      const room = new Room();
      roomRef.current = room;
      room.on(RoomEvent.TrackSubscribed, (track: Track) => {
        if (track.kind === Track.Kind.Audio) document.body.appendChild(track.attach());
      });
      room.on(RoomEvent.TrackUnsubscribed, (track: Track) => {
        track.detach().forEach((el) => el.remove());
      });
      room.on(RoomEvent.Connected, async () => {
        setCallStatus("Connected · Speaking to Saathi");
        try { await room.localParticipant.setMicrophoneEnabled(true); } catch {}
      });
      room.on(RoomEvent.Disconnected, () => {
        setIsCalling(false);
        setCallStatus("Call Ended");
        setTimeout(fetchData, 1500);
      });
      await room.connect(serverUrl, token);
    } catch (e: any) {
      setIsCalling(false);
      setCallStatus("Failed: " + e.message);
    }
  };

  const endCall = () => {
    roomRef.current?.disconnect();
    roomRef.current = null;
    setIsCalling(false);
    setCallStatus("Idle");
  };

  const handleReset = async () => {
    if (confirm("Reset all call records for clean testing?")) {
      await fetch("/api/calls", { method: "DELETE" });
      fetchData();
    }
  };

  const formatDate = (iso: string) => {
    if (!iso) return "-";
    try { return new Date(iso).toLocaleString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit", day: "2-digit", month: "short" }); }
    catch { return iso; }
  };

  const successRate = stats.totalCalls > 0 ? Math.round((stats.successfulCalls / stats.totalCalls) * 100) : 0;

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #060b14; font-family: 'Inter', sans-serif; color: #f9fafb; }
        .db-root { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }

        /* Header */
        .db-header {
          display: flex; align-items: center; justify-content: space-between;
          margin-bottom: 40px; padding-bottom: 24px;
          border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .db-brand { display: flex; align-items: center; gap: 12px; }
        .db-brand-dot { width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981; }
        .db-title { font-size: 22px; font-weight: 900; letter-spacing: -0.5px; }
        .db-sub { font-size: 12px; color: rgba(255,255,255,0.35); margin-top: 2px; }
        .db-header-right { display: flex; align-items: center; gap: 12px; }
        .db-update-text { font-size: 11px; color: rgba(255,255,255,0.25); }
        .db-btn-sm {
          padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);
          background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.5);
          font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s;
        }
        .db-btn-sm:hover { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.8); }
        .db-agent-link {
          display: flex; align-items: center; gap: 6px;
          padding: 8px 16px; border-radius: 8px;
          background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(16,185,129,0.1));
          border: 1px solid rgba(99,102,241,0.3);
          color: #818cf8; font-size: 12px; font-weight: 700;
          text-decoration: none; transition: all 0.2s;
        }
        .db-agent-link:hover { background: rgba(99,102,241,0.25); color: #a5b4fc; }

        /* Stats Grid */
        .db-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
        @media (max-width: 768px) { .db-stats { grid-template-columns: repeat(2, 1fr); } }
        .db-stat-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 16px; padding: 24px 20px;
          text-align: center;
          transition: transform 0.2s, border-color 0.2s;
        }
        .db-stat-card:hover { transform: translateY(-2px); border-color: rgba(255,255,255,0.1); }
        .db-stat-label { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; }
        .db-stat-value { font-size: 44px; font-weight: 900; line-height: 1; margin-bottom: 6px; }
        .db-stat-hint { font-size: 11px; color: rgba(255,255,255,0.25); }

        /* Live Call Panel */
        .db-call-panel {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 16px; padding: 20px 24px;
          display: flex; align-items: center; justify-content: space-between;
          margin-bottom: 28px; gap: 16px;
        }
        .db-call-info h3 { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
        .db-call-status { font-size: 12px; }
        .db-call-btns { display: flex; gap: 10px; flex-shrink: 0; }
        .db-call-btn {
          padding: 11px 22px; border: none; border-radius: 10px;
          font-size: 13px; font-weight: 800; color: #fff; cursor: pointer;
          transition: transform 0.15s, box-shadow 0.15s;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .db-call-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(0,0,0,0.4); }
        .db-call-btn:disabled { opacity: 0.5; cursor: not-allowed; }

        /* Table */
        .db-table-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 16px; overflow: hidden;
        }
        .db-table-header {
          padding: 18px 24px; border-bottom: 1px solid rgba(255,255,255,0.06);
          display: flex; justify-content: space-between; align-items: center;
        }
        .db-table-header h3 { font-size: 15px; font-weight: 700; }
        .db-table-header span { font-size: 12px; color: rgba(255,255,255,0.3); }
        table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
        thead tr { background: rgba(255,255,255,0.03); }
        th { padding: 12px 20px; font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: rgba(255,255,255,0.35); }
        td { padding: 14px 20px; border-bottom: 1px solid rgba(255,255,255,0.04); }
        tbody tr:hover { background: rgba(255,255,255,0.02); }
        tbody tr:last-child td { border-bottom: none; }
        .db-empty { padding: 48px; text-align: center; color: rgba(255,255,255,0.25); font-size: 14px; }
        .badge {
          display: inline-block; padding: 3px 9px; border-radius: 6px;
          font-size: 10px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;
        }
      `}</style>

      <div className="db-root">
        {/* Header */}
        <div className="db-header">
          <div className="db-brand">
            <div className="db-brand-dot" />
            <div>
              <div className="db-title">Performance Dashboard</div>
              <div className="db-sub">Day 8 · Local Commerce Track · Real SQLite Metrics</div>
            </div>
          </div>
          <div className="db-header-right">
            <span className="db-update-text">↻ {lastUpdated || "Syncing..."}</span>
            <button className="db-btn-sm" onClick={handleReset}>Reset DB</button>
            <a href="/" className="db-agent-link">🎙️ Voice Agent</a>
          </div>
        </div>

        {/* Stats */}
        <div className="db-stats">
          <div className="db-stat-card" style={{ borderColor: "rgba(96,165,250,0.2)" }}>
            <div className="db-stat-label" style={{ color: "#60a5fa" }}>Total Calls</div>
            <div className="db-stat-value" style={{ color: "#60a5fa" }}>{stats.totalCalls}</div>
            <div className="db-stat-hint">Browser &amp; SIP Combined</div>
          </div>

          <div className="db-stat-card" style={{ borderColor: "rgba(16,185,129,0.2)" }}>
            <div className="db-stat-label" style={{ color: "#34d399" }}>Successful</div>
            <div className="db-stat-value" style={{ color: "#10b981" }}>{stats.successfulCalls}</div>
            <div className="db-stat-hint">Product Enquiry Done</div>
          </div>

          <div className="db-stat-card" style={{ borderColor: "rgba(239,68,68,0.2)" }}>
            <div className="db-stat-label" style={{ color: "#f87171" }}>Failed</div>
            <div className="db-stat-value" style={{ color: "#ef4444" }}>{stats.failedCalls}</div>
            <div className="db-stat-hint">Dropped / Incomplete</div>
          </div>

          <div className="db-stat-card" style={{ borderColor: "rgba(250,204,21,0.2)" }}>
            <div className="db-stat-label" style={{ color: "#fbbf24" }}>Success Rate</div>
            <div className="db-stat-value" style={{ color: "#f59e0b" }}>{successRate}%</div>
            <div className="db-stat-hint">Enquiry Completion Rate</div>
          </div>
        </div>

        {/* Live Call Launcher */}
        <div className="db-call-panel">
          <div className="db-call-info">
            <h3>📞 Make a Test Call</h3>
            <div
              className="db-call-status"
              style={{ color: isCalling ? "#34d399" : "rgba(255,255,255,0.35)" }}
            >
              Status: {callStatus}
            </div>
          </div>
          <div className="db-call-btns">
            {!isCalling ? (
              <button
                className="db-call-btn"
                style={{ background: "linear-gradient(135deg,#10b981,#059669)" }}
                onClick={startTestCall}
              >
                🎙️ Start Call
              </button>
            ) : (
              <button
                className="db-call-btn"
                style={{ background: "#ef4444" }}
                onClick={endCall}
              >
                🔴 End Call
              </button>
            )}
          </div>
        </div>

        {/* Calls Table */}
        <div className="db-table-card">
          <div className="db-table-header">
            <h3>Recent Calls Log</h3>
            <span>Showing {calls.length} calls · Auto-refreshes every 3s</span>
          </div>

          {loading ? (
            <div className="db-empty">Loading records...</div>
          ) : calls.length === 0 ? (
            <div className="db-empty">
              No calls yet. Start a call from the <a href="/" style={{ color: "#818cf8" }}>Voice Agent</a> or above.
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table>
                <thead>
                  <tr>
                    <th>Call ID</th>
                    <th>Type</th>
                    <th>Duration</th>
                    <th>Outcome</th>
                    <th>Reason</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {calls.map((c, i) => (
                    <tr key={c.id || i}>
                      <td style={{ fontFamily: "monospace", color: "#60a5fa", fontWeight: 600 }}>
                        {c.masked_call_id || c.call_id}
                      </td>
                      <td>
                        <span
                          className="badge"
                          style={{
                            background: c.call_type === "sip" ? "rgba(99,102,241,0.15)" : "rgba(255,255,255,0.07)",
                            color: c.call_type === "sip" ? "#a5b4fc" : "#94a3b8",
                            border: `1px solid ${c.call_type === "sip" ? "rgba(99,102,241,0.3)" : "rgba(255,255,255,0.1)"}`,
                          }}
                        >
                          {c.call_type}
                        </span>
                      </td>
                      <td style={{ color: "#d1d5db" }}>{c.duration ? `${c.duration}s` : "0s"}</td>
                      <td>
                        <span
                          className="badge"
                          style={{
                            background: c.outcome === "successful" ? "rgba(16,185,129,0.12)" : "rgba(239,68,68,0.12)",
                            color: c.outcome === "successful" ? "#34d399" : "#f87171",
                            border: `1px solid ${c.outcome === "successful" ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
                          }}
                        >
                          {c.outcome}
                        </span>
                      </td>
                      <td style={{ color: "rgba(255,255,255,0.4)", maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {c.reason || "-"}
                      </td>
                      <td style={{ color: "rgba(255,255,255,0.3)", fontSize: 12 }}>
                        {formatDate(c.started_at || c.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
