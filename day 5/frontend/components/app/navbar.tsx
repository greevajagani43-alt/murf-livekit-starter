'use client';

import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { ThemeToggle } from '@/components/app/theme-toggle';

interface NavbarProps {
  appConfig: AppConfig;
}

export function Navbar({ appConfig }: NavbarProps) {
  const { isConnected } = useSessionContext();

  return (
    <header className="flex h-14 flex-shrink-0 items-center justify-between border-b border-[#E7E5E0] dark:border-border bg-white dark:bg-card px-4 md:px-6">
      {/* Left: Store name & logo */}
      <div className="flex items-center gap-2.5">
        {/* Store icon — a simple shop glyph */}
        <span className="text-2xl select-none">🏪</span>
        <div className="leading-tight">
          <p className="text-sm font-bold text-[#1C1917] dark:text-foreground tracking-tight">
            Ratan Kirana
          </p>
          <p className="text-[10px] text-[#78716C] dark:text-muted-foreground tracking-wide uppercase hidden sm:block">
            &amp; General Store · Maninagar
          </p>
        </div>
      </div>

      {/* Right: Saathi status + theme toggle */}
      <div className="flex items-center gap-3">
        {/* Saathi online badge */}
        <div className="hidden sm:flex items-center gap-1.5 rounded-full border border-[#E7E5E0] dark:border-border px-3 py-1">
          <span
            className={`inline-block h-2 w-2 rounded-full transition-colors ${
              isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-emerald-400'
            }`}
          />
          <span className="text-xs font-medium text-[#1C1917] dark:text-foreground">
            {isConnected ? 'Saathi is active' : 'Saathi is ready'}
          </span>
        </div>
        {/* Theme toggle — hidden on mobile (shown in footer) */}
        <div className="hidden lg:block">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
