'use client';

import { useEffect, useState } from 'react';
import { ProductCard } from '@/components/app/product-card';
import type { Product } from '@/components/app/product-card';
import { OffersStrip } from '@/components/app/offers';
import { LucideIcon } from '@/components/app/lucide-icon';

// ── Category icon map ──────────────────────────────────────────────────────
// Maps category name → Lucide icon name

const CATEGORY_ICONS: Record<string, string> = {
  'All': 'ShoppingBasket',
  'Atta & Flour': 'Wheat',
  'Rice & Dal': 'Wheat',
  'Oil & Ghee': 'Droplets',
  'Spices': 'Sprout',
  'Tea & Coffee': 'Coffee',
  'Sugar & Sweeteners': 'Candy',
  'Biscuits & Snacks': 'Cookie',
  'Dairy': 'Milk',
  'Beverages': 'GlassWater',
  'Personal Care': 'Bath',
  'Household': 'Sparkles',
};

function categoryIcon(cat: string): string {
  return CATEGORY_ICONS[cat] ?? 'Package';
}

// ── Greeting helper ────────────────────────────────────────────────────────

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

// ── Skeleton loader ────────────────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div className="flex flex-col rounded-xl border border-[#E7E5E0] dark:border-border bg-white dark:bg-card p-3.5 gap-3 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="h-9 w-9 rounded-lg bg-[#E7E5E0] dark:bg-muted" />
        <div className="h-4 w-16 rounded-full bg-[#E7E5E0] dark:bg-muted" />
      </div>
      <div className="space-y-1.5">
        <div className="h-3.5 w-3/4 rounded bg-[#E7E5E0] dark:bg-muted" />
        <div className="h-3 w-1/2 rounded bg-[#E7E5E0] dark:bg-muted" />
      </div>
      <div className="flex justify-between">
        <div className="h-4 w-10 rounded bg-[#E7E5E0] dark:bg-muted" />
        <div className="h-4 w-12 rounded-full bg-[#E7E5E0] dark:bg-muted" />
      </div>
    </div>
  );
}

// ── Component ──────────────────────────────────────────────────────────────

export function Catalogue() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>(['All']);
  const [activeCategory, setActive] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch categories once
  useEffect(() => {
    fetch('/api/categories')
      .then((r) => r.json())
      .then((cats: unknown) => {
        if (Array.isArray(cats)) {
          const normalized = cats.filter(
            (cat): cat is string => typeof cat === 'string' && cat.trim().length > 0
          );
          setCategories(['All', ...normalized]);
        }
      })
      .catch(() => {
        // keep default ['All'] — non-fatal
      });
  }, []);

  // Fetch products when active category changes
  useEffect(() => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams();
    if (activeCategory !== 'All') params.set('category', activeCategory);

    fetch(`/api/products?${params}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: unknown) => {
        setProducts(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('[catalogue] fetch failed:', err);
        setError('Could not load products. Is the backend running?');
        setLoading(false);
      });
  }, [activeCategory]);

  return (
    <div className="px-4 py-5 md:px-6 md:py-6 max-w-4xl mx-auto">
      {/* Welcome */}
      <div className="mb-5">
        <h1 className="text-xl md:text-2xl font-bold text-[#1C1917] dark:text-foreground">
          {getGreeting()} 👋
        </h1>
        <p className="text-sm text-[#78716C] dark:text-muted-foreground mt-1">
          What would you like from Ratan Kirana today?
        </p>
        <p className="text-xs text-[#A8A29E] dark:text-muted-foreground mt-0.5">
          Order naturally with Saathi using your voice →
        </p>
      </div>

      {/* Offer strip */}
      <div className="mb-5">
        <OffersStrip />
      </div>

      {/* Category chips */}
      <div className="mb-5">
        <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] dark:text-muted-foreground mb-2.5">
          Categories
        </p>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat,i) => (
            <button
              key={i}
              onClick={() => setActive(cat)}
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-all ${activeCategory === cat
                  ? 'border-amber-400 bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400'
                  : 'border-[#E7E5E0] dark:border-border bg-white dark:bg-card text-[#57534E] dark:text-muted-foreground hover:border-amber-300 dark:hover:border-amber-800'
                }`}
            >
              <LucideIcon
                name={categoryIcon(cat)}
                size={12}
                className={
                  activeCategory === cat
                    ? 'text-amber-600 dark:text-amber-400'
                    : 'text-[#78716C] dark:text-muted-foreground'
                }
              />
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Product grid */}
      <div>
        <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] dark:text-muted-foreground mb-2.5">
          {activeCategory === 'All' ? 'All Products' : activeCategory}
          {!loading && (
            <span className="ml-2 font-normal normal-case tracking-normal text-[#C4C0BA] dark:text-muted-foreground/60">
              ({products.length})
            </span>
          )}
        </p>

        {/* Error state */}
        {error && (
          <div className="rounded-lg border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 px-4 py-3 text-xs text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        {/* Loading skeletons */}
        {loading && !error && (
          <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* Product grid */}
        {!loading && !error && (
          <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-3">
            {products.map((product, idx) => (
              <ProductCard
                key={product.id ?? `${product.name}-${idx}`}
                product={product}
              />
            ))}
          </div>
        )}
      </div>

      {/* Mobile footer spacer */}
      <div className="h-6 lg:h-0" />
    </div>
  );
}