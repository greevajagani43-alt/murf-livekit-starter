'use client';

import { TagIcon } from 'lucide-react';

export function OffersStrip() {
  return (
    <div className="rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-950/30 px-4 py-3 flex items-start gap-3">
      <div className="mt-0.5 flex-shrink-0 h-7 w-7 rounded-full bg-amber-100 dark:bg-amber-900/50 flex items-center justify-center">
        <TagIcon size={14} className="text-amber-600 dark:text-amber-400" />
      </div>
      <div>
        <p className="text-xs font-bold uppercase tracking-wide text-amber-700 dark:text-amber-400 mb-0.5">
          Today's Offer
        </p>
        <p className="text-sm font-semibold text-[#1C1917] dark:text-foreground">
          Buy 2 Aashirvaad Atta 5kg — get ₹30 off
        </p>
        <p className="text-xs text-[#78716C] dark:text-muted-foreground mt-0.5">
          Valid today only · Ask Saathi to add it to your order
        </p>
      </div>
      <span className="ml-auto flex-shrink-0 text-xs font-bold bg-amber-500 text-white rounded-full px-2.5 py-1">
        LIVE
      </span>
    </div>
  );
}
