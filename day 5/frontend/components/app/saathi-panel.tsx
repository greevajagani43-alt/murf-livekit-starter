'use client';

import { useEffect, useRef, useState } from 'react';
import { useTheme } from 'next-themes';
import { useAgent, useSessionContext, useSessionMessages } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';
import { AudioVisualizer } from '@/components/agents-ui/blocks/agent-session-view-01/components/audio-visualizer';
import { Shimmer } from '@/components/ai-elements/shimmer';
import { ProductCard } from '@/components/app/product-card';
import type { Product } from '@/components/app/product-card';

// ── Product mention extraction ─────────────────────────────────────────────
// Scans agent message text for product names from a locally-cached product
// list (fetched once from /api/products) and returns matches.

function extractMentionedProducts(text: string, catalogue: Product[]): Product[] {
  if (!text || !catalogue.length) return [];
  const lower = text.toLowerCase();
  const seen = new Set<string>();
  const found: Product[] = [];

  for (const p of catalogue) {
    const key = `${p.name}|${p.size}`;
    if (!seen.has(key) && lower.includes(p.name.toLowerCase())) {
      seen.add(key);
      found.push(p);
      if (found.length >= 3) break; // cap at 3 per message to avoid spam
    }
  }
  return found;
}

// ── Agent state label ──────────────────────────────────────────────────────

function agentStateLabel(state?: string): { text: string; colour: string } {
  switch (state) {
    case 'listening':
      return { text: 'Saathi is listening…', colour: 'text-emerald-600 dark:text-emerald-400' };
    case 'thinking':
      return { text: 'Saathi is thinking…', colour: 'text-amber-600 dark:text-amber-400' };
    case 'speaking':
      return { text: 'Saathi is speaking…', colour: 'text-amber-600 dark:text-amber-400' };
    case 'connecting':
      return { text: 'Connecting…', colour: 'text-[#78716C] dark:text-muted-foreground' };
    default:
      return { text: 'Ready to help', colour: 'text-[#A8A29E] dark:text-muted-foreground' };
  }
}

// ── Conversation message ───────────────────────────────────────────────────
// Renders one chat message + any inline product chips beneath agent messages.

interface MessageRowProps {
  text: string;
  isLocal: boolean;
  mentionedProducts: Product[];
}

function MessageRow({ text, isLocal, mentionedProducts }: MessageRowProps) {
  return (
    <div className={`flex flex-col gap-1.5 ${isLocal ? 'items-end' : 'items-start'}`}>
      {/* Bubble */}
      <div
        className={`max-w-[90%] rounded-2xl px-3 py-2 text-xs leading-relaxed ${isLocal
            ? 'bg-amber-500 text-white rounded-br-sm'
            : 'bg-[#F5F0E8] dark:bg-muted text-[#1C1917] dark:text-foreground rounded-bl-sm'
          }`}
      >
        {text}
      </div>

      {/* Horizontal product chips — only on agent messages */}
      {!isLocal && mentionedProducts.length > 0 && (
        <div className="flex flex-col gap-1.5 w-full max-w-[92%]">
          {mentionedProducts.map((p, i) => (
            <ProductCard key={`${p.name}-${p.size}-${i}`} product={p} compact />
          ))}
        </div>
      )}
    </div>
  );
}

// ── Saathi Panel ───────────────────────────────────────────────────────────

interface SaathiPanelProps {
  appConfig: AppConfig;
}

export function SaathiPanel({ appConfig }: SaathiPanelProps) {
  const { resolvedTheme } = useTheme();
  const session = useSessionContext();
  const { messages } = useSessionMessages(session);
  const { state: agentState } = useAgent();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Local product catalogue for mention matching
  const [catalogue, setCatalogue] = useState<Product[]>([]);

  useEffect(() => {
    // Fetch once on mount — used only for mention extraction, no auth needed
    fetch('/api/products')
      .then((r) => r.json())
      .then((data: unknown) => {
        if (Array.isArray(data)) setCatalogue(data);
        // else: no chips — non-fatal
      })
      .catch(() => {
        // Non-fatal — product chips just won't appear
      });
  }, []);

  // Auto-scroll to bottom when messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const vizColor =
    resolvedTheme === 'dark'
      ? (appConfig.audioVisualizerColorDark ?? '#FCD34D')
      : (appConfig.audioVisualizerColor ?? '#D97706');

  const stateLabel = agentStateLabel(agentState);

  const controls = {
    leave: true,
    microphone: true,
    chat: false,
    camera: false,
    screenShare: false,
  };

  return (
    <div className="flex h-full w-full flex-col bg-[#FAFAF7] dark:bg-background">
      {/* ── Panel header ─────────────────────────────────────────────────── */}
      <div className="flex-shrink-0 border-b border-[#E7E5E0] dark:border-border px-4 py-3.5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-950/50 text-base select-none">
            🎙️
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-bold text-[#1C1917] dark:text-foreground leading-none">
              Saathi
            </p>
            <p className="mt-0.5 text-[11px] text-[#78716C] dark:text-muted-foreground leading-none">
              Your Ratan Kirana voice assistant
            </p>
          </div>
          <span className="h-2.5 w-2.5 flex-shrink-0 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </div>

      {/* ── Audio visualizer ─────────────────────────────────────────────── */}
      <div className="flex-shrink-0 flex flex-col items-center justify-center py-5 gap-2">
        <div className="h-[100px] w-full flex items-center justify-center">
          <AudioVisualizer
            audioVisualizerType={appConfig.audioVisualizerType ?? 'wave'}
            audioVisualizerColor={vizColor as `#${string}`}
            audioVisualizerWaveLineWidth={appConfig.audioVisualizerWaveLineWidth ?? 2}
            isChatOpen={false}
            className="h-[100px] w-full"
          />
        </div>
        <p className={`text-xs font-medium ${stateLabel.colour}`}>{stateLabel.text}</p>
      </div>

      {/* ── Conversation + product chips ─────────────────────────────────── */}
      <div
        ref={scrollRef}
        className="flex-1 min-h-0 overflow-y-auto border-t border-[#E7E5E0] dark:border-border px-3 py-3 flex flex-col gap-2.5"
      >
        {messages.length === 0 ? (
          /* Empty state */
          <div className="flex h-full flex-col items-center justify-center text-center gap-2">
            <span className="text-3xl select-none">🛒</span>
            <Shimmer
              duration={2.5}
              className="text-xs text-[#A8A29E] dark:text-muted-foreground max-w-[180px]"
            >
              {session.isConnected
                ? 'Saathi is listening — ask about any product or place an order'
                : 'Press the button below to start talking'}
            </Shimmer>
          </div>
        ) : (
          messages.map((msg) => {
            const isLocal = msg.from?.isLocal === true;
            const mentioned = isLocal
              ? []
              : extractMentionedProducts(msg.message, catalogue);

            return (
              <MessageRow
                key={msg.id}
                text={msg.message}
                isLocal={isLocal}
                mentionedProducts={mentioned}
              />
            );
          })
        )}
      </div>

      {/* ── Controls ─────────────────────────────────────────────────────── */}
      <div className="flex-shrink-0 border-t border-[#E7E5E0] dark:border-border bg-white dark:bg-card px-4 py-3">
        {!session.isConnected ? (
          <button
            onClick={session.start}
            className="w-full rounded-full bg-amber-500 hover:bg-amber-600 active:scale-95 transition-all py-3 text-sm font-bold text-white shadow-sm"
          >
            🎙️ {appConfig.startButtonText ?? 'Baat karo Saathi se'}
          </button>
        ) : (
          <AgentControlBar
            variant="livekit"
            controls={controls}
            isChatOpen={false}
            isConnected={session.isConnected}
            onDisconnect={session.end}
            onIsChatOpenChange={() => { }}
          />
        )}
      </div>

      {/* ── Delivery info ─────────────────────────────────────────────────── */}
      <div className="flex-shrink-0 px-4 pb-4">
        <div className="rounded-lg bg-[#F5F0E8] dark:bg-muted px-3 py-2 text-[11px] text-[#78716C] dark:text-muted-foreground text-center">
          🛵 Free delivery above ₹300 · COD / GPay / PhonePe / Paytm
        </div>
      </div>
    </div>
  );
}