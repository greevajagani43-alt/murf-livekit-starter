'use client';

import { LucideIcon } from "./lucide-icon";


export interface Product {
  id?: number;
  name: string;
  size: string;
  price: number;
  /** Lucide PascalCase icon name, e.g. "Wheat", "Coffee" */
  icon: string;
  category: string;
  qty?: number;
}

interface ProductCardProps {
  product: Product;
  /** Compact horizontal layout used inside Saathi panel mentions */
  compact?: boolean;
}

export function ProductCard({ product, compact = false }: ProductCardProps) {
  const isLowStock = product.qty !== undefined && product.qty <= 5;
  const isOutOfStock = product.qty !== undefined && product.qty === 0;

  if (compact) {
    // ── Horizontal chip variant for Saathi panel ───────────────────────────
    return (
      <div className="flex items-center gap-2.5 rounded-lg border border-[#E7E5E0] dark:border-border bg-white dark:bg-card px-3 py-2 select-none">
        {/* Icon bubble */}
        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-md bg-amber-500 dark:bg-amber-600">
          <LucideIcon name={product.icon} size={16} className="text-white" />
        </div>
        {/* Info */}
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs font-semibold text-[#1C1917] dark:text-foreground leading-tight">
            {product.name}
          </p>
          <p className="text-[11px] text-[#A8A29E] dark:text-muted-foreground">{product.size}</p>
        </div>
        {/* Price */}
        <span className="flex-shrink-0 text-xs font-bold text-amber-600 dark:text-amber-400">
          ₹{product.price}
        </span>
      </div>
    );
  }

  // ── Full grid card variant ─────────────────────────────────────────────
  return (
    <div
      className={`relative flex flex-col rounded-xl border bg-white dark:bg-card p-3.5 gap-2 hover:shadow-sm transition-all cursor-default select-none ${
        isOutOfStock
          ? 'border-red-200 dark:border-red-900/50 opacity-70'
          : 'border-[#E7E5E0] dark:border-border hover:border-amber-300 dark:hover:border-amber-700'
      }`}
    >
      {/* Icon area */}
      <div className="flex items-center justify-between">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500 dark:bg-amber-600">
          <LucideIcon name={product.icon} size={18} className="text-white" />
        </div>
        <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-[#F5F0E8] dark:bg-muted text-[#78716C] dark:text-muted-foreground">
          {product.category}
        </span>
      </div>

      {/* Name + size */}
      <div>
        <p className="text-sm font-semibold text-[#1C1917] dark:text-foreground leading-snug">
          {product.name}
        </p>
        <p className="text-xs text-[#A8A29E] dark:text-muted-foreground">{product.size}</p>
      </div>

      {/* Price row */}
      <div className="flex items-center justify-between mt-auto">
        <p className="text-sm font-bold text-amber-600 dark:text-amber-400">₹{product.price}</p>
        {/* Stock badge */}
        {product.qty !== undefined && (
          <span
            className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
              isOutOfStock
                ? 'bg-red-100 dark:bg-red-950/40 text-red-600 dark:text-red-400'
                : isLowStock
                ? 'bg-orange-100 dark:bg-orange-950/40 text-orange-600 dark:text-orange-400'
                : 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400'
            }`}
          >
            {isOutOfStock ? 'Out' : `${product.qty} left`}
          </span>
        )}
      </div>
    </div>
  );
}
