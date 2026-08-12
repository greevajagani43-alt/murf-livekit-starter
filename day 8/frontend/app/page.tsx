"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { Room, RoomEvent, Track, LocalAudioTrack } from "livekit-client";

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

export default function PerformanceDashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalCalls: 0,
    successfulCalls: 0,
    failedCalls: 0,
  });
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  // Live Call State
  const [isCalling, setIsCalling] = useState<boolean>(false);
  const [callStatus, setCallStatus] = useState<string>("Idle");
  const roomRef = useRef<Room | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      const [statsRes, callsRes] = await Promise.all([
        fetch("/api/dashboard/stats", { cache: "no-store" }),
        fetch("/api/calls", { cache: "no-store" }),
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats({
          totalCalls: statsData.totalCalls ?? 0,
          successfulCalls: statsData.successfulCalls ?? 0,
          failedCalls: statsData.failedCalls ?? 0,
        });
      }

      if (callsRes.ok) {
        const callsData = await callsRes.json();
        if (Array.isArray(callsData)) {
          setCalls(callsData);
        }
      }

      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Poll database statistics every 3 seconds
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 3000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  // Start live test call directly from browser
  const startTestCall = async () => {
    if (isCalling) return;
    setIsCalling(true);
    setCallStatus("Connecting to Saathi...");

    try {
      const roomName = `browser_call_${Date.now()}`;
      const tokenRes = await fetch(`/api/token?roomName=${roomName}`);
      if (!tokenRes.ok) throw new Error("Failed to generate LiveKit token");
      const { token, serverUrl } = await tokenRes.json();

      const room = new Room();
      roomRef.current = room;

      room.on(RoomEvent.Connected, async () => {
        setCallStatus("Connected · Speaking to Saathi (Local Commerce Track)");
        // Publish microphone
        try {
          const micTrack = await LocalAudioTrack.create();
          await room.localParticipant.publishTrack(micTrack);
        } catch (e) {
          console.warn("Microphone access pending/denied:", e);
        }
      });

      room.on(RoomEvent.Disconnected, () => {
        setCallStatus("Call Ended");
        setIsCalling(false);
        // Refresh dashboard stats after call completes
        setTimeout(fetchDashboardData, 1500);
      });

      await room.connect(serverUrl, token);
    } catch (err: any) {
      alert(`Call failed to connect: ${err.message}`);
      setIsCalling(false);
      setCallStatus("Idle");
    }
  };

  const disconnectCall = () => {
    if (roomRef.current) {
      roomRef.current.disconnect();
      roomRef.current = null;
    }
    setIsCalling(false);
    setCallStatus("Call Disconnected");
  };

  const handleReset = async () => {
    if (confirm("Reset call database for clean test verification?")) {
      await fetch("/api/calls", { method: "DELETE" });
      await fetchDashboardData();
    }
  };

  const formatDate = (isoString: string) => {
    if (!isoString) return "-";
    try {
      return new Date(isoString).toLocaleString("en-IN", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        day: "2-digit",
        month: "short",
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 20px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 32,
          paddingBottom: 20,
          borderBottom: "1px solid #1f293d",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: 26,
              fontWeight: 800,
              letterSpacing: "0.5px",
              color: "#ffffff",
              marginBottom: 4,
            }}
          >
            VOICE AGENT PERFORMANCE
          </h1>
          <p style={{ color: "#9ca3af", fontSize: 14 }}>
            Local Commerce Track · Murf Falcon TTS · Real SQLite Database Metrics
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 6 }}>
            Auto-refreshing every 3s · Last: {lastUpdated || "Syncing..."}
          </div>
          <button
            onClick={handleReset}
            style={{
              background: "#1f2937",
              color: "#9ca3af",
              border: "1px solid #374151",
              borderRadius: 6,
              padding: "6px 12px",
              fontSize: 12,
              cursor: "pointer",
            }}
          >
            Reset Test DB
          </button>
        </div>
      </div>

      {/* Primary Metrics Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 20,
          marginBottom: 36,
        }}
      >
        {/* TOTAL CALLS */}
        <div
          style={{
            background: "#111827",
            border: "1px solid #1f2937",
            borderRadius: 12,
            padding: "24px 28px",
            textAlign: "center",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.3)",
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 700,
              color: "#9ca3af",
              letterSpacing: "1px",
              marginBottom: 8,
            }}
          >
            TOTAL CALLS
          </div>
          <div
            style={{
              fontSize: 48,
              fontWeight: 900,
              color: "#60a5fa",
              lineHeight: 1,
            }}
          >
            {stats.totalCalls}
          </div>
          <div style={{ fontSize: 11, color: "#6b7280", marginTop: 8 }}>
            Total Browser & SIP Calls Recorded
          </div>
        </div>

        {/* SUCCESSFUL CALLS */}
        <div
          style={{
            background: "#111827",
            border: "1px solid #065f46",
            borderRadius: 12,
            padding: "24px 28px",
            textAlign: "center",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.3)",
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 700,
              color: "#34d399",
              letterSpacing: "1px",
              marginBottom: 8,
            }}
          >
            SUCCESSFUL CALLS
          </div>
          <div
            style={{
              fontSize: 48,
              fontWeight: 900,
              color: "#10b981",
              lineHeight: 1,
            }}
          >
            {stats.successfulCalls}
          </div>
          <div style={{ fontSize: 11, color: "#059669", marginTop: 8 }}>
            Product Enquiry Completed
          </div>
        </div>

        {/* FAILED CALLS */}
        <div
          style={{
            background: "#111827",
            border: "1px solid #991b1b",
            borderRadius: 12,
            padding: "24px 28px",
            textAlign: "center",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.3)",
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 700,
              color: "#f87171",
              letterSpacing: "1px",
              marginBottom: 8,
            }}
          >
            FAILED CALLS
          </div>
          <div
            style={{
              fontSize: 48,
              fontWeight: 900,
              color: "#ef4444",
              lineHeight: 1,
            }}
          >
            {stats.failedCalls}
          </div>
          <div style={{ fontSize: 11, color: "#dc2626", marginTop: 8 }}>
            Enquiry Incomplete / Dropped Call
          </div>
        </div>
      </div>

      {/* Interactive Voice Call Launcher */}
      <div
        style={{
          background: "#111827",
          border: "1px solid #1f2937",
          borderRadius: 12,
          padding: 24,
          marginBottom: 36,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 4 }}>
            📞 Make a Real Test Call
          </h2>
          <p style={{ fontSize: 13, color: "#9ca3af" }}>
            Status: <span style={{ color: isCalling ? "#34d399" : "#d1d5db" }}>{callStatus}</span>
          </p>
        </div>

        <div style={{ display: "flex", gap: 12 }}>
          {!isCalling ? (
            <button
              onClick={startTestCall}
              style={{
                background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                color: "#ffffff",
                border: "none",
                borderRadius: 8,
                padding: "12px 24px",
                fontSize: 14,
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.2)",
              }}
            >
              🎙️ Baat Karo Saathi Se (Start Call)
            </button>
          ) : (
            <button
              onClick={disconnectCall}
              style={{
                background: "#ef4444",
                color: "#ffffff",
                border: "none",
                borderRadius: 8,
                padding: "12px 24px",
                fontSize: 14,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              🔴 End Call
            </button>
          )}
        </div>
      </div>

      {/* Recent Calls Table */}
      <div
        style={{
          background: "#111827",
          border: "1px solid #1f2937",
          borderRadius: 12,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "18px 24px",
            borderBottom: "1px solid #1f2937",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "#f9fafb" }}>
            Recent Calls Log
          </h3>
          <span style={{ fontSize: 12, color: "#6b7280" }}>
            Showing last {calls.length} calls (Anonymized)
          </span>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: "center", color: "#9ca3af" }}>
            Loading call records...
          </div>
        ) : calls.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "#6b7280" }}>
            No calls recorded yet in SQLite database. Click "Start Call" above or dial via SIP to generate real call data!
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: 13,
                textAlign: "left",
              }}
            >
              <thead>
                <tr
                  style={{
                    background: "#1f2937",
                    color: "#9ca3af",
                    textTransform: "uppercase",
                    fontSize: 11,
                    letterSpacing: "0.5px",
                  }}
                >
                  <th style={{ padding: "12px 20px" }}>Call ID</th>
                  <th style={{ padding: "12px 20px" }}>Type</th>
                  <th style={{ padding: "12px 20px" }}>Duration</th>
                  <th style={{ padding: "12px 20px" }}>Outcome</th>
                  <th style={{ padding: "12px 20px" }}>Reason / Outcome Detail</th>
                  <th style={{ padding: "12px 20px" }}>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {calls.map((c, idx) => (
                  <tr
                    key={c.id || idx}
                    style={{
                      borderBottom: "1px solid #1f2937",
                      background: idx % 2 === 0 ? "#111827" : "#0f1623",
                    }}
                  >
                    {/* Anonymized Call ID */}
                    <td
                      style={{
                        padding: "14px 20px",
                        fontFamily: "monospace",
                        color: "#60a5fa",
                        fontWeight: 600,
                      }}
                    >
                      {c.masked_call_id || c.call_id}
                    </td>

                    {/* Type */}
                    <td style={{ padding: "14px 20px" }}>
                      <span
                        style={{
                          background: c.call_type === "sip" ? "#312e81" : "#1e293b",
                          color: c.call_type === "sip" ? "#a5b4fc" : "#94a3b8",
                          padding: "3px 8px",
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: 700,
                          textTransform: "uppercase",
                        }}
                      >
                        {c.call_type}
                      </span>
                    </td>

                    {/* Duration */}
                    <td style={{ padding: "14px 20px", color: "#d1d5db" }}>
                      {c.duration ? `${c.duration}s` : "0s"}
                    </td>

                    {/* Outcome Badge */}
                    <td style={{ padding: "14px 20px" }}>
                      <span
                        style={{
                          background:
                            c.outcome === "successful" ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                          color: c.outcome === "successful" ? "#34d399" : "#f87171",
                          border: `1px solid ${
                            c.outcome === "successful" ? "#059669" : "#dc2626"
                          }`,
                          padding: "4px 10px",
                          borderRadius: 6,
                          fontSize: 11,
                          fontWeight: 800,
                          textTransform: "uppercase",
                          letterSpacing: "0.5px",
                        }}
                      >
                        {c.outcome}
                      </span>
                    </td>

                    {/* Reason */}
                    <td style={{ padding: "14px 20px", color: "#9ca3af" }}>
                      {c.reason || "-"}
                    </td>

                    {/* Time */}
                    <td
                      style={{
                        padding: "14px 20px",
                        color: "#6b7280",
                        fontSize: 12,
                      }}
                    >
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
  );
}
