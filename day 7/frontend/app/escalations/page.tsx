"use client";

import { useEffect, useState, useCallback } from "react";

interface Escalation {
  escalation_id: string;
  user_id: string;
  customer_name: string;
  reason: string;
  urgency: string;
  summary: string;
  what_agent_checked: string;
  language: string;
  preferred_followup: string;
  status: string;
  email_sent: number;
  created_at: string;
  updated_at: string;
}

const URGENCY_CONFIG: Record<
  string,
  { label: string; color: string; bg: string; dot: string }
> = {
  emergency: {
    label: "🔴 EMERGENCY",
    color: "#ef4444",
    bg: "#fef2f2",
    dot: "#ef4444",
  },
  high: { label: "🟠 HIGH", color: "#f97316", bg: "#fff7ed", dot: "#f97316" },
  medium: {
    label: "🟡 MEDIUM",
    color: "#eab308",
    bg: "#fefce8",
    dot: "#eab308",
  },
  low: { label: "🟢 LOW", color: "#22c55e", bg: "#f0fdf4", dot: "#22c55e" },
};

const REASON_LABELS: Record<string, string> = {
  payment_dispute: "💳 Payment Dispute",
  refund_request: "💰 Refund Request",
  order_dispute: "📦 Order Dispute",
};

const STATUS_CONFIG: Record<
  string,
  { label: string; bg: string; color: string }
> = {
  open: { label: "🔓 Open", bg: "#dbeafe", color: "#1d4ed8" },
  in_progress: { label: "⚙️ In Progress", bg: "#fef9c3", color: "#854d0e" },
  resolved: { label: "✅ Resolved", bg: "#dcfce7", color: "#166534" },
};

const LANG_LABELS: Record<string, string> = {
  en: "English",
  hi: "हिंदी",
  gu: "ગુજરાતી",
};

export default function EscalationsDashboard() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<string | null>(null);
  const [selected, setSelected] = useState<Escalation | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchEscalations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const url =
        filter === "all"
          ? "/api/escalations"
          : `/api/escalations?status=${filter}`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) throw new Error("Failed to load escalations");
      const data = await res.json();
      setEscalations(data);
      setLastRefresh(new Date());
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(msg + " — Is the escalations server running on port 8002?");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchEscalations();
    const interval = setInterval(fetchEscalations, 15000);
    return () => clearInterval(interval);
  }, [fetchEscalations]);

  const updateStatus = async (id: string, status: string) => {
    setUpdating(id);
    try {
      const res = await fetch(`/api/escalations/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error("Update failed");
      await fetchEscalations();
      if (selected?.escalation_id === id) {
        const updated = escalations.find((e) => e.escalation_id === id);
        if (updated) setSelected({ ...updated, status });
      }
    } catch (e) {
      alert("Failed to update status");
    } finally {
      setUpdating(null);
    }
  };

  const fmt = (iso: string) =>
    new Date(iso + "Z").toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  const counts = {
    all: escalations.length,
    open: escalations.filter((e) => e.status === "open").length,
    in_progress: escalations.filter((e) => e.status === "in_progress").length,
    resolved: escalations.filter((e) => e.status === "resolved").length,
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#e2e8f0" }}>
      {/* Header */}
      <header
        style={{
          background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
          borderBottom: "1px solid #334155",
          padding: "20px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 28 }}>🛒</span>
            <div>
              <h1
                style={{
                  margin: 0,
                  fontSize: 22,
                  fontWeight: 700,
                  color: "#f1f5f9",
                  letterSpacing: "-0.5px",
                }}
              >
                Ratan Kirana — Escalation Dashboard
              </h1>
              <p
                style={{
                  margin: "2px 0 0",
                  fontSize: 13,
                  color: "#94a3b8",
                }}
              >
                Saathi Voice Agent · Human-Help Requests
              </p>
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 12, color: "#64748b" }}>
            Auto-refresh every 15s · Last:{" "}
            {lastRefresh.toLocaleTimeString("en-IN")}
          </span>
          <button
            onClick={fetchEscalations}
            style={{
              background: "#D97706",
              color: "white",
              border: "none",
              borderRadius: 8,
              padding: "8px 16px",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            ↻ Refresh
          </button>
        </div>
      </header>

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 32px" }}>
        {/* Stats Row */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 16,
            marginBottom: 28,
          }}
        >
          {[
            { key: "open", label: "Open", icon: "🔓", color: "#3b82f6" },
            { key: "in_progress", label: "In Progress", icon: "⚙️", color: "#eab308" },
            { key: "resolved", label: "Resolved", icon: "✅", color: "#22c55e" },
            { key: "all", label: "Total", icon: "📋", color: "#a855f7" },
          ].map((s) => (
            <div
              key={s.key}
              onClick={() => setFilter(s.key)}
              style={{
                background:
                  filter === s.key
                    ? "rgba(217, 119, 6, 0.12)"
                    : "rgba(30,41,59,0.8)",
                border: `1px solid ${filter === s.key ? "#D97706" : "#334155"}`,
                borderRadius: 12,
                padding: "18px 20px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              <div style={{ fontSize: 24, marginBottom: 6 }}>{s.icon}</div>
              <div
                style={{
                  fontSize: 32,
                  fontWeight: 700,
                  color: s.color,
                  lineHeight: 1,
                }}
              >
                {counts[s.key as keyof typeof counts]}
              </div>
              <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              background: "#450a0a",
              border: "1px solid #ef4444",
              borderRadius: 10,
              padding: 16,
              marginBottom: 20,
              color: "#fca5a5",
              fontSize: 14,
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Escalations List */}
        {loading ? (
          <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>⏳</div>
            Loading escalations…
          </div>
        ) : escalations.length === 0 ? (
          <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🎉</div>
            <div style={{ fontSize: 18, fontWeight: 600, color: "#94a3b8" }}>
              No escalations
            </div>
            <div style={{ fontSize: 14, marginTop: 6 }}>
              {filter === "all"
                ? "All conversations are going smoothly!"
                : `No ${filter.replace("_", " ")} requests.`}
            </div>
          </div>
        ) : (
          <div style={{ display: "flex", gap: 20 }}>
            {/* List */}
            <div style={{ flex: 1, minWidth: 0 }}>
              {escalations.map((esc) => {
                const urg = URGENCY_CONFIG[esc.urgency] || URGENCY_CONFIG.medium;
                const st = STATUS_CONFIG[esc.status] || STATUS_CONFIG.open;
                return (
                  <div
                    key={esc.escalation_id}
                    onClick={() =>
                      setSelected(
                        selected?.escalation_id === esc.escalation_id
                          ? null
                          : esc
                      )
                    }
                    style={{
                      background:
                        selected?.escalation_id === esc.escalation_id
                          ? "rgba(217, 119, 6, 0.08)"
                          : "rgba(30,41,59,0.7)",
                      border: `1px solid ${selected?.escalation_id === esc.escalation_id ? "#D97706" : "#334155"}`,
                      borderLeft: `4px solid ${urg.color}`,
                      borderRadius: 10,
                      padding: "16px 20px",
                      marginBottom: 12,
                      cursor: "pointer",
                      transition: "all 0.2s",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        justifyContent: "space-between",
                        gap: 12,
                      }}
                    >
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            marginBottom: 6,
                            flexWrap: "wrap",
                          }}
                        >
                          <span
                            style={{
                              fontFamily: "monospace",
                              fontSize: 13,
                              color: "#D97706",
                              fontWeight: 700,
                            }}
                          >
                            {esc.escalation_id}
                          </span>
                          <span
                            style={{
                              background: urg.bg,
                              color: urg.color,
                              borderRadius: 5,
                              padding: "2px 8px",
                              fontSize: 11,
                              fontWeight: 700,
                            }}
                          >
                            {urg.label}
                          </span>
                          <span
                            style={{
                              background: st.bg,
                              color: st.color,
                              borderRadius: 5,
                              padding: "2px 8px",
                              fontSize: 11,
                              fontWeight: 600,
                            }}
                          >
                            {st.label}
                          </span>
                          {esc.email_sent ? (
                            <span
                              style={{
                                background: "#f0fdf4",
                                color: "#166534",
                                borderRadius: 5,
                                padding: "2px 8px",
                                fontSize: 11,
                              }}
                            >
                              📧 Email Sent
                            </span>
                          ) : (
                            <span
                              style={{
                                background: "#fef9c3",
                                color: "#854d0e",
                                borderRadius: 5,
                                padding: "2px 8px",
                                fontSize: 11,
                              }}
                            >
                              📧 No Email
                            </span>
                          )}
                        </div>

                        <div
                          style={{
                            fontWeight: 700,
                            fontSize: 16,
                            color: "#f1f5f9",
                            marginBottom: 4,
                          }}
                        >
                          {esc.customer_name}
                        </div>
                        <div
                          style={{
                            fontSize: 13,
                            color: "#94a3b8",
                            marginBottom: 6,
                          }}
                        >
                          {REASON_LABELS[esc.reason] || esc.reason} ·{" "}
                          {LANG_LABELS[esc.language] || esc.language} · Prefers:{" "}
                          {esc.preferred_followup}
                        </div>
                        <div
                          style={{
                            fontSize: 13,
                            color: "#cbd5e1",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {esc.summary}
                        </div>
                      </div>

                      <div
                        style={{
                          fontSize: 12,
                          color: "#64748b",
                          whiteSpace: "nowrap",
                          textAlign: "right",
                        }}
                      >
                        {fmt(esc.created_at)}
                      </div>
                    </div>

                    {/* Quick actions */}
                    {esc.status !== "resolved" && (
                      <div
                        style={{
                          display: "flex",
                          gap: 8,
                          marginTop: 12,
                          flexWrap: "wrap",
                        }}
                        onClick={(ev) => ev.stopPropagation()}
                      >
                        {esc.status === "open" && (
                          <button
                            onClick={() =>
                              updateStatus(esc.escalation_id, "in_progress")
                            }
                            disabled={updating === esc.escalation_id}
                            style={actionBtnStyle("#854d0e", "#fef9c3")}
                          >
                            {updating === esc.escalation_id
                              ? "Updating…"
                              : "⚙️ Mark In Progress"}
                          </button>
                        )}
                        <button
                          onClick={() =>
                            updateStatus(esc.escalation_id, "resolved")
                          }
                          disabled={updating === esc.escalation_id}
                          style={actionBtnStyle("#166534", "#dcfce7")}
                        >
                          {updating === esc.escalation_id
                            ? "Updating…"
                            : "✅ Mark Resolved"}
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Detail Panel */}
            {selected && (
              <div
                style={{
                  width: 340,
                  flexShrink: 0,
                  background: "rgba(30,41,59,0.9)",
                  border: "1px solid #334155",
                  borderRadius: 12,
                  padding: 20,
                  alignSelf: "flex-start",
                  position: "sticky",
                  top: 20,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: 16,
                  }}
                >
                  <h3
                    style={{ margin: 0, fontSize: 15, color: "#f1f5f9" }}
                  >
                    Request Detail
                  </h3>
                  <button
                    onClick={() => setSelected(null)}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#64748b",
                      cursor: "pointer",
                      fontSize: 18,
                    }}
                  >
                    ×
                  </button>
                </div>

                <DetailRow label="Reference ID" value={selected.escalation_id} mono />
                <DetailRow label="Customer" value={selected.customer_name} />
                <DetailRow label="User ID" value={selected.user_id} mono />
                <DetailRow
                  label="Reason"
                  value={REASON_LABELS[selected.reason] || selected.reason}
                />
                <DetailRow
                  label="Urgency"
                  value={URGENCY_CONFIG[selected.urgency]?.label || selected.urgency}
                />
                <DetailRow
                  label="Status"
                  value={STATUS_CONFIG[selected.status]?.label || selected.status}
                />
                <DetailRow
                  label="Language"
                  value={LANG_LABELS[selected.language] || selected.language}
                />
                <DetailRow
                  label="Follow-up"
                  value={selected.preferred_followup}
                />
                <DetailRow
                  label="Email"
                  value={selected.email_sent ? "✅ Sent" : "❌ Not sent"}
                />
                <DetailRow label="Created" value={fmt(selected.created_at)} />
                <DetailRow label="Updated" value={fmt(selected.updated_at)} />

                <div style={{ marginTop: 16, marginBottom: 8 }}>
                  <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>
                    ISSUE SUMMARY
                  </div>
                  <div
                    style={{
                      background: "#1e293b",
                      borderRadius: 8,
                      padding: 12,
                      fontSize: 13,
                      color: "#cbd5e1",
                      lineHeight: 1.5,
                    }}
                  >
                    {selected.summary}
                  </div>
                </div>

                {selected.what_agent_checked && (
                  <div style={{ marginBottom: 8 }}>
                    <div
                      style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}
                    >
                      AGENT ALREADY CHECKED
                    </div>
                    <div
                      style={{
                        background: "#1e293b",
                        borderRadius: 8,
                        padding: 12,
                        fontSize: 13,
                        color: "#94a3b8",
                        lineHeight: 1.5,
                      }}
                    >
                      {selected.what_agent_checked}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function DetailRow({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "6px 0",
        borderBottom: "1px solid #1e293b",
        gap: 8,
      }}
    >
      <span style={{ fontSize: 12, color: "#64748b", flexShrink: 0 }}>
        {label}
      </span>
      <span
        style={{
          fontSize: 12,
          color: "#e2e8f0",
          fontFamily: mono ? "monospace" : undefined,
          textAlign: "right",
          wordBreak: "break-all",
        }}
      >
        {value}
      </span>
    </div>
  );
}

function actionBtnStyle(color: string, bg: string): React.CSSProperties {
  return {
    background: bg,
    color: color,
    border: `1px solid ${color}`,
    borderRadius: 6,
    padding: "5px 12px",
    fontSize: 12,
    fontWeight: 600,
    cursor: "pointer",
  };
}
