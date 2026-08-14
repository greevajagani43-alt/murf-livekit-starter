'use client';

import { useEffect, useState, useCallback } from 'react';

// ── Types ─────────────────────────────────────────────────────────────────

interface CallStats {
  total: number;
  successful: number;
  failed: number;
}

interface CallRecord {
  call_id: string;
  channel: string;
  outcome: string;
  failure_reason: string | null;
  duration_seconds: number;
  created_at: string;
}

// ── API Config ────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_PRODUCTS_API_URL || 'http://localhost:8001';

// ── Helpers ───────────────────────────────────────────────────────────────

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso + 'Z'); // Treat as UTC
    return d.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return iso;
  }
}

function getSuccessRate(stats: CallStats): string {
  if (stats.total === 0) return '0';
  return ((stats.successful / stats.total) * 100).toFixed(1);
}

// ── Dashboard Page ────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [stats, setStats] = useState<CallStats>({ total: 0, successful: 0, failed: 0 });
  const [recentCalls, setRecentCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, callsRes] = await Promise.all([
        fetch(`${API_BASE}/api/call-stats`),
        fetch(`${API_BASE}/api/recent-calls?limit=20`),
      ]);

      if (!statsRes.ok || !callsRes.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const statsData = await statsRes.json();
      const callsData = await callsRes.json();

      setStats(statsData);
      setRecentCalls(callsData);
      setError(null);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection error');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch + auto-refresh every 10 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const successRate = getSuccessRate(stats);

  // SVG donut chart parameters
  const donutRadius = 54;
  const donutCircumference = 2 * Math.PI * donutRadius;
  const successPct = stats.total > 0 ? stats.successful / stats.total : 0;
  const failPct = stats.total > 0 ? stats.failed / stats.total : 0;
  const successOffset = donutCircumference * (1 - successPct);
  const failOffset = donutCircumference * (1 - failPct);
  const failRotation = successPct * 360;

  return (
    <div className="min-h-screen bg-[var(--ratan-bg)] dark:bg-[var(--background)] text-[var(--ratan-text)] dark:text-[var(--foreground)]">
      {/* Header */}
      <header className="border-b border-[var(--ratan-border)] dark:border-[var(--border)] bg-white/70 dark:bg-[var(--card)]/70 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/25">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">Call Analytics</h1>
              <p className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">
                Ratan Kirana &amp; General Store
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="/"
              className="text-sm px-4 py-2 rounded-lg bg-[var(--ratan-surface)] dark:bg-[var(--secondary)] hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors font-medium"
            >
              ← Back to Store
            </a>
            <div className="flex items-center gap-2 text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              Live · {lastRefresh.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm flex items-center gap-2">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <span>Could not connect to backend API at {API_BASE}. Make sure the server is running.</span>
            <button onClick={fetchData} className="ml-auto font-medium underline hover:no-underline">Retry</button>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-32">
            <div className="flex flex-col items-center gap-4">
              <div className="w-10 h-10 border-3 border-amber-500/30 border-t-amber-500 rounded-full animate-spin"></div>
              <p className="text-sm text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">Loading dashboard…</p>
            </div>
          </div>
        ) : (
          <>
            {/* Success Definition Banner */}
            <div className="mb-8 p-4 rounded-xl bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/50">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-amber-900 dark:text-amber-200">Success Definition</p>
                  <p className="text-sm text-amber-800 dark:text-amber-300/80 mt-0.5">
                    A <strong>successful call</strong> = the customer completes an order (place_order returns success). 
                    A <strong>failed call</strong> = the session ends without a completed order.
                  </p>
                </div>
              </div>
            </div>

            {/* Stats Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
              {/* Total Calls */}
              <div className="group relative overflow-hidden rounded-2xl bg-white dark:bg-[var(--card)] border border-[var(--ratan-border)] dark:border-[var(--border)] p-6 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-0.5">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-blue-500/5 to-transparent dark:from-blue-500/10 rounded-bl-full"></div>
                <div className="relative">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-9 h-9 rounded-xl bg-blue-50 dark:bg-blue-950/40 flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
                      </svg>
                    </div>
                    <span className="text-sm font-medium text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">Total Calls</span>
                  </div>
                  <p className="text-4xl font-bold tracking-tight text-blue-600 dark:text-blue-400">{stats.total}</p>
                  <p className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] mt-1">All voice sessions recorded</p>
                </div>
              </div>

              {/* Successful Calls */}
              <div className="group relative overflow-hidden rounded-2xl bg-white dark:bg-[var(--card)] border border-[var(--ratan-border)] dark:border-[var(--border)] p-6 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-0.5">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-emerald-500/5 to-transparent dark:from-emerald-500/10 rounded-bl-full"></div>
                <div className="relative">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 flex items-center justify-center">
                      <svg className="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <span className="text-sm font-medium text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">Successful</span>
                  </div>
                  <p className="text-4xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400">{stats.successful}</p>
                  <p className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] mt-1">Orders placed successfully</p>
                </div>
              </div>

              {/* Failed Calls */}
              <div className="group relative overflow-hidden rounded-2xl bg-white dark:bg-[var(--card)] border border-[var(--ratan-border)] dark:border-[var(--border)] p-6 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-0.5">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-rose-500/5 to-transparent dark:from-rose-500/10 rounded-bl-full"></div>
                <div className="relative">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-9 h-9 rounded-xl bg-rose-50 dark:bg-rose-950/40 flex items-center justify-center">
                      <svg className="w-5 h-5 text-rose-600 dark:text-rose-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <span className="text-sm font-medium text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">Failed</span>
                  </div>
                  <p className="text-4xl font-bold tracking-tight text-rose-600 dark:text-rose-400">{stats.failed}</p>
                  <p className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] mt-1">No order completed</p>
                </div>
              </div>
            </div>

            {/* Success Rate + Recent Calls Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Success Rate Donut */}
              <div className="rounded-2xl bg-white dark:bg-[var(--card)] border border-[var(--ratan-border)] dark:border-[var(--border)] p-6 shadow-sm">
                <h2 className="text-sm font-semibold mb-4 text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] uppercase tracking-wider">Success Rate</h2>
                <div className="flex flex-col items-center">
                  <div className="relative w-36 h-36">
                    <svg viewBox="0 0 128 128" className="w-full h-full -rotate-90">
                      {/* Background ring */}
                      <circle
                        cx="64" cy="64" r={donutRadius}
                        fill="none"
                        stroke="currentColor"
                        className="text-gray-100 dark:text-gray-800"
                        strokeWidth="12"
                      />
                      {/* Success arc (green) */}
                      {stats.total > 0 && (
                        <circle
                          cx="64" cy="64" r={donutRadius}
                          fill="none"
                          stroke="currentColor"
                          className="text-emerald-500 dark:text-emerald-400 transition-all duration-700 ease-out"
                          strokeWidth="12"
                          strokeDasharray={donutCircumference}
                          strokeDashoffset={successOffset}
                          strokeLinecap="round"
                        />
                      )}
                      {/* Failed arc (rose) */}
                      {stats.total > 0 && stats.failed > 0 && (
                        <circle
                          cx="64" cy="64" r={donutRadius}
                          fill="none"
                          stroke="currentColor"
                          className="text-rose-400 dark:text-rose-500 transition-all duration-700 ease-out"
                          strokeWidth="12"
                          strokeDasharray={donutCircumference}
                          strokeDashoffset={failOffset}
                          strokeLinecap="round"
                          style={{ transform: `rotate(${failRotation}deg)`, transformOrigin: '64px 64px' }}
                        />
                      )}
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-3xl font-bold">{successRate}%</span>
                      <span className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">success</span>
                    </div>
                  </div>
                  <div className="flex gap-6 mt-5 text-xs">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                      <span className="text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">Successful ({stats.successful})</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                      <span className="text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">Failed ({stats.failed})</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Calls Table */}
              <div className="lg:col-span-2 rounded-2xl bg-white dark:bg-[var(--card)] border border-[var(--ratan-border)] dark:border-[var(--border)] shadow-sm overflow-hidden">
                <div className="p-5 pb-3 flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] uppercase tracking-wider">Recent Calls</h2>
                  <span className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">{recentCalls.length} records</span>
                </div>

                {recentCalls.length === 0 ? (
                  <div className="px-5 pb-8 pt-4 text-center">
                    <div className="w-14 h-14 rounded-2xl bg-gray-50 dark:bg-gray-800 flex items-center justify-center mx-auto mb-3">
                      <svg className="w-7 h-7 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 3.75v4.5m0-4.5h-4.5m4.5 0l-6 6m3 12c-8.284 0-15-6.716-15-15V4.5A2.25 2.25 0 014.5 2.25h1.372c.516 0 .966.351 1.091.852l1.106 4.423c.11.44-.054.902-.417 1.173l-1.293.97a1.062 1.062 0 00-.38 1.21 12.035 12.035 0 007.143 7.143c.441.162.928-.004 1.21-.38l.97-1.293a1.125 1.125 0 011.173-.417l4.423 1.106c.5.125.852.575.852 1.091V19.5a2.25 2.25 0 01-2.25 2.25h-2.25z" />
                      </svg>
                    </div>
                    <p className="text-sm text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)]">No calls recorded yet</p>
                    <p className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] mt-1 opacity-70">
                      Make a call with Saathi to see data here
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-t border-b border-[var(--ratan-border)] dark:border-[var(--border)] bg-gray-50/50 dark:bg-white/[0.02]">
                          <th className="text-left px-5 py-2.5 font-medium text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] text-xs">Time</th>
                          <th className="text-left px-5 py-2.5 font-medium text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] text-xs">Channel</th>
                          <th className="text-left px-5 py-2.5 font-medium text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] text-xs">Outcome</th>
                          <th className="text-left px-5 py-2.5 font-medium text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] text-xs">Duration</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentCalls.map((call, i) => (
                          <tr
                            key={call.call_id}
                            className={`border-b border-[var(--ratan-border)]/50 dark:border-[var(--border)]/50 hover:bg-gray-50/80 dark:hover:bg-white/[0.02] transition-colors ${
                              i === 0 ? 'animate-[fadeIn_0.4s_ease-out]' : ''
                            }`}
                          >
                            <td className="px-5 py-3 text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] whitespace-nowrap">
                              {formatTime(call.created_at)}
                            </td>
                            <td className="px-5 py-3 whitespace-nowrap">
                              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                                call.channel === 'sip'
                                  ? 'bg-purple-50 dark:bg-purple-950/30 text-purple-700 dark:text-purple-300'
                                  : 'bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-300'
                              }`}>
                                {call.channel === 'sip' ? '📞 SIP' : '🌐 Browser'}
                              </span>
                            </td>
                            <td className="px-5 py-3 whitespace-nowrap">
                              <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                                call.outcome === 'success'
                                  ? 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300'
                                  : 'bg-rose-50 dark:bg-rose-950/30 text-rose-700 dark:text-rose-300'
                              }`}>
                                {call.outcome === 'success' ? '✓ Success' : '✗ Failed'}
                              </span>
                            </td>
                            <td className="px-5 py-3 text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] font-mono text-xs whitespace-nowrap">
                              {formatDuration(call.duration_seconds)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Privacy Notice */}
            <div className="mt-8 text-center">
              <p className="text-xs text-[var(--ratan-muted)] dark:text-[var(--muted-foreground)] opacity-60">
                🔒 This dashboard does not display passwords, OTPs, PINs, account numbers, medical details, or conversation transcripts.
              </p>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
