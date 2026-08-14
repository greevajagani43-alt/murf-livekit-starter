"use client";

import React, { useEffect, useState, useRef } from "react";
import { Room, RoomEvent, Track } from "livekit-client";

type CallState = "idle" | "connecting" | "connected" | "ended";

export default function VoiceAgentPage() {
  const [callState, setCallState] = useState<CallState>("idle");
  const [statusMsg, setStatusMsg] = useState("Tap to speak with Saathi");
  const [transcript, setTranscript] = useState<{ role: string; text: string }[]>([]);
  const [pulse, setPulse] = useState(false);
  const roomRef = useRef<Room | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll transcript
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [transcript]);

  const startCall = async () => {
    if (callState !== "idle" && callState !== "ended") return;
    setCallState("connecting");
    setStatusMsg("Connecting to Saathi...");
    setTranscript([]);

    try {
      const roomName = `browser_call_${Date.now()}`;
      const res = await fetch(`/api/token?roomName=${roomName}`);
      if (!res.ok) throw new Error("Token generation failed");
      const { token, serverUrl } = await res.json();

      const room = new Room();
      roomRef.current = room;

      room.on(RoomEvent.TrackSubscribed, (track: Track) => {
        if (track.kind === Track.Kind.Audio) {
          const el = track.attach();
          document.body.appendChild(el);
        }
      });

      room.on(RoomEvent.TrackUnsubscribed, (track: Track) => {
        track.detach().forEach((el) => el.remove());
      });

      room.on(RoomEvent.Connected, async () => {
        setCallState("connected");
        setStatusMsg("Connected · Saathi is listening...");
        setPulse(true);
        try {
          await room.localParticipant.setMicrophoneEnabled(true);
        } catch (e) {
          console.warn("Mic access denied:", e);
        }
      });

      // Listen for data messages (transcripts)
      room.on(RoomEvent.DataReceived, (payload: Uint8Array) => {
        try {
          const decoded = JSON.parse(new TextDecoder().decode(payload));
          if (decoded.type === "transcript") {
            setTranscript((prev) => [...prev, { role: decoded.role, text: decoded.text }]);
          }
        } catch {}
      });

      room.on(RoomEvent.Disconnected, () => {
        setCallState("ended");
        setStatusMsg("Call ended · Thank you!");
        setPulse(false);
      });

      await room.connect(serverUrl, token);
      setTranscript([{ role: "saathi", text: "Namaste! Welcome to Ratan Kirana Store. How can I help you today?" }]);
    } catch (err: any) {
      setCallState("idle");
      setStatusMsg("Connection failed. Try again.");
      setPulse(false);
    }
  };

  const endCall = () => {
    if (roomRef.current) {
      roomRef.current.disconnect();
      roomRef.current = null;
    }
    setCallState("ended");
    setStatusMsg("Call ended · Thank you!");
    setPulse(false);
  };

  const resetCall = () => {
    setCallState("idle");
    setStatusMsg("Tap to speak with Saathi");
    setTranscript([]);
  };

  const btnLabel =
    callState === "idle" ? "🎙️ Start Call"
    : callState === "connecting" ? "Connecting..."
    : callState === "connected" ? "🔴 End Call"
    : "🔄 New Call";

  const btnAction =
    callState === "idle" ? startCall
    : callState === "connecting" ? () => {}
    : callState === "connected" ? endCall
    : resetCall;

  const btnColor =
    callState === "idle" ? "linear-gradient(135deg,#10b981,#059669)"
    : callState === "connecting" ? "linear-gradient(135deg,#6366f1,#4f46e5)"
    : callState === "connected" ? "linear-gradient(135deg,#ef4444,#dc2626)"
    : "linear-gradient(135deg,#3b82f6,#2563eb)";

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #060b14; font-family: 'Inter', sans-serif; min-height: 100vh; }

        .va-root {
          min-height: 100vh;
          background: radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.12) 0%, transparent 50%),
                      radial-gradient(ellipse at 80% 80%, rgba(16,185,129,0.08) 0%, transparent 50%),
                      #060b14;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 24px;
        }

        .va-card {
          width: 100%;
          max-width: 520px;
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 28px;
          padding: 40px 36px 36px;
          box-shadow: 0 32px 80px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08);
          backdrop-filter: blur(20px);
          position: relative;
          overflow: hidden;
        }
        .va-card::before {
          content: '';
          position: absolute;
          top: -1px; left: -1px; right: -1px;
          height: 2px;
          background: linear-gradient(90deg, transparent, rgba(99,102,241,0.6), rgba(16,185,129,0.6), transparent);
          border-radius: 28px 28px 0 0;
        }

        .va-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 32px;
        }
        .va-logo-dot {
          width: 10px; height: 10px;
          background: #10b981;
          border-radius: 50%;
          box-shadow: 0 0 10px #10b981;
        }
        .va-logo-text {
          font-size: 13px;
          font-weight: 700;
          letter-spacing: 2px;
          color: rgba(255,255,255,0.4);
          text-transform: uppercase;
        }

        .va-avatar-wrap {
          display: flex;
          justify-content: center;
          margin-bottom: 28px;
        }
        .va-avatar {
          position: relative;
          width: 110px; height: 110px;
          display: flex; align-items: center; justify-content: center;
        }
        .va-avatar-ring {
          position: absolute;
          width: 110px; height: 110px;
          border-radius: 50%;
          border: 2px solid rgba(16,185,129,0.3);
          animation: none;
        }
        .va-avatar-ring.pulse {
          animation: ring-pulse 1.8s ease-out infinite;
        }
        @keyframes ring-pulse {
          0%   { transform: scale(1);   opacity: 0.7; border-color: rgba(16,185,129,0.6); }
          100% { transform: scale(1.6); opacity: 0;   border-color: rgba(16,185,129,0); }
        }
        .va-avatar-ring2 {
          position: absolute;
          width: 110px; height: 110px;
          border-radius: 50%;
          border: 2px solid rgba(99,102,241,0.2);
          animation: none;
        }
        .va-avatar-ring2.pulse {
          animation: ring-pulse2 1.8s ease-out 0.6s infinite;
        }
        @keyframes ring-pulse2 {
          0%   { transform: scale(1);   opacity: 0.5; border-color: rgba(99,102,241,0.4); }
          100% { transform: scale(1.8); opacity: 0;   border-color: rgba(99,102,241,0); }
        }
        .va-avatar-circle {
          width: 90px; height: 90px;
          background: linear-gradient(135deg, #1e293b, #0f172a);
          border-radius: 50%;
          border: 2px solid rgba(255,255,255,0.1);
          display: flex; align-items: center; justify-content: center;
          font-size: 38px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.4);
          position: relative; z-index: 1;
        }

        .va-name {
          text-align: center;
          font-size: 28px;
          font-weight: 900;
          color: #ffffff;
          letter-spacing: -0.5px;
          margin-bottom: 6px;
        }
        .va-subtitle {
          text-align: center;
          font-size: 13px;
          color: rgba(255,255,255,0.4);
          margin-bottom: 8px;
        }
        .va-status {
          text-align: center;
          font-size: 13px;
          font-weight: 600;
          margin-bottom: 28px;
          min-height: 20px;
          transition: color 0.3s;
        }

        /* Waveform bars */
        .va-wave {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          height: 36px;
          margin-bottom: 28px;
        }
        .va-wave-bar {
          width: 4px;
          border-radius: 2px;
          background: rgba(99,102,241,0.3);
          height: 8px;
          transition: background 0.3s;
        }
        .va-wave.active .va-wave-bar {
          background: #10b981;
          animation: wave-bar 0.9s ease-in-out infinite;
        }
        .va-wave-bar:nth-child(1) { animation-delay: 0.0s; }
        .va-wave-bar:nth-child(2) { animation-delay: 0.1s; }
        .va-wave-bar:nth-child(3) { animation-delay: 0.2s; }
        .va-wave-bar:nth-child(4) { animation-delay: 0.3s; }
        .va-wave-bar:nth-child(5) { animation-delay: 0.4s; }
        .va-wave-bar:nth-child(6) { animation-delay: 0.5s; }
        .va-wave-bar:nth-child(7) { animation-delay: 0.6s; }
        .va-wave-bar:nth-child(8) { animation-delay: 0.7s; }
        .va-wave-bar:nth-child(9) { animation-delay: 0.8s; }
        @keyframes wave-bar {
          0%, 100% { height: 6px; }
          50%       { height: 28px; }
        }

        /* CTA Button */
        .va-btn {
          width: 100%;
          padding: 16px;
          border: none;
          border-radius: 14px;
          font-size: 15px;
          font-weight: 800;
          color: #fff;
          cursor: pointer;
          letter-spacing: 0.5px;
          transition: transform 0.15s, box-shadow 0.15s;
          box-shadow: 0 4px 20px rgba(0,0,0,0.3);
          margin-bottom: 16px;
        }
        .va-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 8px 28px rgba(0,0,0,0.4); }
        .va-btn:active:not(:disabled) { transform: translateY(0); }
        .va-btn:disabled { opacity: 0.6; cursor: not-allowed; }

        /* Transcript box */
        .va-transcript {
          background: rgba(0,0,0,0.3);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 14px;
          padding: 16px;
          max-height: 180px;
          overflow-y: auto;
          margin-bottom: 20px;
          scrollbar-width: thin;
          scrollbar-color: rgba(255,255,255,0.1) transparent;
        }
        .va-transcript::-webkit-scrollbar { width: 4px; }
        .va-transcript::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        .va-msg { display: flex; gap: 8px; margin-bottom: 10px; align-items: flex-start; }
        .va-msg:last-child { margin-bottom: 0; }
        .va-msg-label {
          font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
          padding: 2px 6px; border-radius: 4px; white-space: nowrap; margin-top: 2px;
          min-width: 52px; text-align: center;
        }
        .va-msg-label.saathi { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
        .va-msg-label.you { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.2); }
        .va-msg-text { font-size: 13px; color: rgba(255,255,255,0.75); line-height: 1.5; }

        .va-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .va-footer-badge {
          display: flex; align-items: center; gap: 6px;
          font-size: 11px; color: rgba(255,255,255,0.25);
        }
        .va-footer-badge span { color: rgba(255,255,255,0.4); font-weight: 600; }
        .va-dash-link {
          font-size: 11px; font-weight: 600;
          color: rgba(99,102,241,0.7);
          text-decoration: none;
          padding: 4px 10px;
          border: 1px solid rgba(99,102,241,0.2);
          border-radius: 6px;
          transition: all 0.2s;
        }
        .va-dash-link:hover { color: #818cf8; border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.08); }

        .va-products {
          display: flex; flex-wrap: wrap; gap: 6px;
          margin-bottom: 24px;
          justify-content: center;
        }
        .va-product-chip {
          font-size: 11px; color: rgba(255,255,255,0.35);
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 20px; padding: 4px 10px;
        }
      `}</style>

      <div className="va-root">
        <div className="va-card">
          {/* Logo / Brand */}
          <div className="va-logo">
            <div className="va-logo-dot" />
            <div className="va-logo-text">Ratan Kirana Store · Day 8</div>
            <a href="/dashboard" className="va-dash-link" style={{ marginLeft: "auto" }}>
              📊 Dashboard →
            </a>
          </div>

          {/* Avatar */}
          <div className="va-avatar-wrap">
            <div className="va-avatar">
              <div className={`va-avatar-ring ${pulse ? "pulse" : ""}`} />
              <div className={`va-avatar-ring2 ${pulse ? "pulse" : ""}`} />
              <div className="va-avatar-circle">🧑‍💼</div>
            </div>
          </div>

          {/* Name & Subtitle */}
          <div className="va-name">Saathi</div>
          <div className="va-subtitle">Your AI Shopping Assistant · Murf Falcon TTS</div>

          {/* Status */}
          <div
            className="va-status"
            style={{
              color:
                callState === "connected" ? "#34d399"
                : callState === "connecting" ? "#818cf8"
                : callState === "ended" ? "#f87171"
                : "rgba(255,255,255,0.45)",
            }}
          >
            {statusMsg}
          </div>

          {/* Product chips */}
          {callState === "idle" && (
            <div className="va-products">
              {["🌾 Atta", "🛢 Oil", "🥛 Milk", "🍚 Rice", "🫘 Dal", "🎧 Headphones", "🧂 Salt"].map((p) => (
                <div key={p} className="va-product-chip">{p}</div>
              ))}
            </div>
          )}

          {/* Waveform */}
          <div className={`va-wave ${pulse ? "active" : ""}`}>
            {[...Array(9)].map((_, i) => (
              <div key={i} className="va-wave-bar" style={{ animationDelay: `${i * 0.1}s` }} />
            ))}
          </div>

          {/* Transcript */}
          {transcript.length > 0 && (
            <div className="va-transcript" ref={scrollRef}>
              {transcript.map((m, i) => (
                <div key={i} className="va-msg">
                  <div className={`va-msg-label ${m.role}`}>{m.role === "saathi" ? "Saathi" : "You"}</div>
                  <div className="va-msg-text">{m.text}</div>
                </div>
              ))}
            </div>
          )}

          {/* CTA Button */}
          <button
            className="va-btn"
            style={{ background: btnColor }}
            onClick={btnAction}
            disabled={callState === "connecting"}
          >
            {btnLabel}
          </button>

          {/* Footer */}
          <div className="va-footer">
            <div className="va-footer-badge">
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: callState === "connected" ? "#10b981" : "rgba(255,255,255,0.15)" }} />
              <span>Deepgram Nova-3 STT</span>
              <span style={{ color: "rgba(255,255,255,0.15)" }}>·</span>
              <span>Murf Falcon TTS</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
