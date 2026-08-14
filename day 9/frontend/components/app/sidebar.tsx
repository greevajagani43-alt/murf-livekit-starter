'use client';

import { useState } from 'react';
import {
  HomeIcon,
  ShoppingBasketIcon,
  TagIcon,
  ClipboardListIcon,
  StoreIcon,
  SettingsIcon,
} from 'lucide-react';
import { cn } from '@/lib/shadcn/utils';

interface NavItem {
  label: string;
  icon: React.ReactNode;
  active?: boolean;
  soon?: boolean;
}

const TOP_ITEMS: NavItem[] = [
  { label: 'Home', icon: <HomeIcon size={16} />, active: true },
  { label: 'Catalogue', icon: <ShoppingBasketIcon size={16} />, soon: false },
  { label: 'Offers', icon: <TagIcon size={16} />, soon: false },
  { label: 'Orders', icon: <ClipboardListIcon size={16} />, soon: true },
];

const BOTTOM_ITEMS: NavItem[] = [
  { label: 'Store Info', icon: <StoreIcon size={16} /> },
  { label: 'Settings', icon: <SettingsIcon size={16} /> },
];

function NavLink({ item, active }: { item: NavItem; active: boolean }) {
  return (
    <button
      className={cn(
        'flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors',
        active
          ? 'bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400 font-semibold'
          : 'text-[#57534E] dark:text-muted-foreground hover:bg-[#F5F0E8] dark:hover:bg-muted hover:text-[#1C1917] dark:hover:text-foreground',
        item.soon && 'opacity-50 cursor-not-allowed'
      )}
      disabled={item.soon}
    >
      <span className={active ? 'text-amber-600 dark:text-amber-400' : ''}>{item.icon}</span>
      <span>{item.label}</span>
      {item.soon && (
        <span className="ml-auto text-[10px] font-medium bg-[#E7E5E0] dark:bg-muted text-[#78716C] dark:text-muted-foreground rounded px-1.5 py-0.5">
          Soon
        </span>
      )}
    </button>
  );
}

export function Sidebar() {
  const [active, setActive] = useState('Home');

  return (
    <div className="flex w-full flex-col gap-1 px-3 py-4">
      {/* Store name block */}
      <div className="mb-3 px-3 py-2">
        <p className="text-[10px] font-bold uppercase tracking-widest text-[#A8A29E] dark:text-muted-foreground">
          Navigation
        </p>
      </div>

      {/* Top nav */}
      <nav className="flex flex-col gap-0.5">
        {TOP_ITEMS.map((item) => (
          <div key={item.label} onClick={() => !item.soon && setActive(item.label)}>
            <NavLink item={item} active={active === item.label} />
          </div>
        ))}
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Divider */}
      <div className="my-2 h-px bg-[#E7E5E0] dark:bg-border" />

      {/* Bottom nav */}
      <nav className="flex flex-col gap-0.5">
        {BOTTOM_ITEMS.map((item) => (
          <NavLink key={item.label} item={item} active={false} />
        ))}
      </nav>

      {/* Store hours chip */}
      <div className="mt-3 rounded-lg border border-[#E7E5E0] dark:border-border bg-[#F5F0E8] dark:bg-muted px-3 py-2.5">
        <p className="text-[11px] font-semibold text-[#44403C] dark:text-foreground">Open today</p>
        <p className="text-[11px] text-[#78716C] dark:text-muted-foreground">8 AM – 10 PM</p>
        <p className="mt-1.5 text-[10px] text-amber-600 dark:text-amber-400 font-medium">
          🛵 Free delivery above ₹300
        </p>
      </div>
    </div>
  );
}
