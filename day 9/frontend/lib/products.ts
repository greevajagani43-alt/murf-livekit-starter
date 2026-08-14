/**
 * lib/products.ts
 * ───────────────
 * Server-side utility that fetches product data from the Python FastAPI
 * products server (products_server.py).
 *
 * Gate-check: if the products server is unreachable, falls back to the
 * hardcoded FALLBACK_PRODUCTS so the UI never completely breaks.
 *
 * Environment variable:
 *   PRODUCTS_API_URL  (default: http://localhost:8001)
 */

export interface Product {
  id?: number;
  name: string;
  size: string;
  price: number;
  icon: string;
  category: string;
  qty?: number;
}

const PRODUCTS_API = process.env.PRODUCTS_API_URL ?? 'http://localhost:8001';

// ── Fallback data (mirrors agent SYSTEM_PROMPT) ────────────────────────────
// Used when the products server is unreachable. Matches the DB seed so
// the UI is still usable during local dev before the backend starts.

const FALLBACK_PRODUCTS: Product[] = [
  { name: 'Aashirvaad Atta',        size: '5 kg',   price: 295, icon: 'Wheat',      category: 'Atta & Flour' },
  { name: 'Fortune Chakki Atta',    size: '5 kg',   price: 285, icon: 'Wheat',      category: 'Atta & Flour' },
  { name: 'India Gate Basmati',     size: '5 kg',   price: 650, icon: 'Wheat',      category: 'Rice & Dal'   },
  { name: 'Toor Dal',               size: '1 kg',   price: 180, icon: 'Wheat',      category: 'Rice & Dal'   },
  { name: 'Fortune Sunflower Oil',  size: '1 L',    price: 145, icon: 'Droplets',   category: 'Oil & Ghee'   },
  { name: 'Amul Ghee',              size: '1 L',    price: 650, icon: 'Milk',       category: 'Oil & Ghee'   },
  { name: 'Tata Salt',              size: '1 kg',   price:  28, icon: 'Waves',      category: 'Spices'       },
  { name: 'Tata Tea Premium',       size: '500 g',  price: 280, icon: 'Coffee',     category: 'Tea & Coffee' },
  { name: 'Nescafe Classic',        size: '100 g',  price: 320, icon: 'Coffee',     category: 'Tea & Coffee' },
  { name: 'Parle-G Biscuits',       size: '800 g',  price: 100, icon: 'Cookie',     category: 'Biscuits & Snacks' },
  { name: 'Haldiram Aloo Bhujia',   size: '200 g',  price:  70, icon: 'Cookie',     category: 'Biscuits & Snacks' },
  { name: 'Amul Butter',            size: '100 g',  price:  60, icon: 'Milk',       category: 'Dairy'        },
  { name: 'Amul Cheese Slices',     size: '200 g',  price: 140, icon: 'Milk',       category: 'Dairy'        },
  { name: 'Amul Taaza Milk',        size: '1 L',    price:  65, icon: 'Milk',       category: 'Dairy'        },
  { name: 'Coca-Cola',              size: '750 ml', price:  45, icon: 'GlassWater', category: 'Beverages'    },
  { name: 'Dove Bathing Soap',      size: '100 g',  price:  55, icon: 'Bath',       category: 'Personal Care'},
  { name: 'Surf Excel Matic',       size: '2 kg',   price: 390, icon: 'Sparkles',   category: 'Household'    },
  { name: 'Dettol Liquid',          size: '250 ml', price:  95, icon: 'ShieldCheck',category: 'Household'    },
];

// ── Helpers ────────────────────────────────────────────────────────────────

interface FetchOptions {
  q?: string;
  category?: string;
}

/**
 * Fetch products from the FastAPI products server.
 * Falls back to FALLBACK_PRODUCTS if the server is unreachable.
 *
 * This runs **server-side** (Next.js API route or server component).
 * Do not import in client components — use /api/products fetch instead.
 */
export async function getProductsFromDB(opts: FetchOptions = {}): Promise<Product[]> {
  const url = new URL(`${PRODUCTS_API}/products`);
  if (opts.q)        url.searchParams.set('q', opts.q);
  if (opts.category) url.searchParams.set('category', opts.category);

  try {
    const res = await fetch(url.toString(), {
      next: { revalidate: 0 }, // no caching — live stock data
    });

    if (!res.ok) {
      console.warn(`[products] API returned ${res.status} — using fallback`);
      return FALLBACK_PRODUCTS;
    }

    const data: Product[] = await res.json();
    return data;
  } catch (err) {
    // Server unreachable (backend not started yet, etc.)
    console.warn('[products] API unreachable — using fallback:', err);
    return FALLBACK_PRODUCTS;
  }
}

/**
 * Fetch distinct category names.
 * Falls back to a derived list from FALLBACK_PRODUCTS if unreachable.
 */
export async function getCategoriesFromDB(): Promise<string[]> {
  try {
    const res = await fetch(`${PRODUCTS_API}/categories`, {
      next: { revalidate: 60 }, // categories change rarely
    });

    if (!res.ok) throw new Error(`status ${res.status}`);
    return await res.json();
  } catch {
    // derive from fallback
    const cats = Array.from(new Set(FALLBACK_PRODUCTS.map((p) => p.category)));
    return cats.sort();
  }
}
