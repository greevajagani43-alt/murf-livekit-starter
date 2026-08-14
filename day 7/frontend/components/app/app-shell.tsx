'use client';

import type { AppConfig } from '@/app-config';
import { Navbar } from '@/components/app/navbar';
import { Sidebar } from '@/components/app/sidebar';
import { Catalogue } from '@/components/app/catalogue';
import { SaathiPanel } from '@/components/app/saathi-panel';
import { ThemeToggle } from '@/components/app/theme-toggle';

interface AppShellProps {
  appConfig: AppConfig;
}

export function AppShell({ appConfig }: AppShellProps) {
  return (
    <div className="flex h-svh flex-col overflow-hidden" style={{ background: '#FAFAF7' }}>
      {/* Navbar */}
      <Navbar appConfig={appConfig} />

      {/* Main three-column layout */}
      <div className="flex min-h-0 flex-1">
        {/* Sidebar — hidden on small screens, shown md+ */}
        <aside className="hidden md:flex md:w-52 lg:w-56 flex-shrink-0 border-r border-[#E7E5E0] dark:border-border">
          <Sidebar />
        </aside>

        {/* Centre main content */}
        <main className="flex-1 overflow-y-auto">
          <Catalogue />
        </main>

        {/* Saathi right panel — hidden on small screens */}
        <aside className="hidden lg:flex lg:w-80 xl:w-96 flex-shrink-0 border-l border-[#E7E5E0] dark:border-border">
          <SaathiPanel appConfig={appConfig} />
        </aside>
      </div>

      {/* Mobile footer bar: Saathi access + theme toggle */}
      <div className="lg:hidden flex items-center justify-between border-t border-[#E7E5E0] dark:border-border px-4 py-2 bg-[#FAFAF7] dark:bg-background">
        <MobileSaathiDrawer appConfig={appConfig} />
        <ThemeToggle />
      </div>
    </div>
  );
}

// ── Mobile Saathi Drawer ─────────────────────────────────────────────────────

import { useState } from 'react';
import { MicIcon, X } from 'lucide-react';

function MobileSaathiDrawer({ appConfig }: { appConfig: AppConfig }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-sm active:scale-95 transition-transform"
      >
        <MicIcon size={16} />
        Saathi
      </button>

      {/* Drawer backdrop */}
      {open && (
        <div className="fixed inset-0 z-50 flex flex-col">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setOpen(false)}
          />
          <div className="relative mt-auto flex flex-col bg-[#FAFAF7] dark:bg-background rounded-t-2xl shadow-xl"
               style={{ height: '75dvh' }}>
            <div className="flex items-center justify-between px-4 py-3 border-b border-[#E7E5E0] dark:border-border">
              <span className="font-semibold text-sm">Saathi — Voice Assistant</span>
              <button onClick={() => setOpen(false)} className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/10">
                <X size={18} />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <SaathiPanel appConfig={appConfig} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
