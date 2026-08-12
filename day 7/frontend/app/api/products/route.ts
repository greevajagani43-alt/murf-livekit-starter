/**
 * app/api/products/route.ts
 * ─────────────────────────
 * Proxies the FastAPI products server so the frontend never talks to it
 * directly (avoids CORS complexity in production).
 *
 * GET /api/products            → all products
 * GET /api/products?q=atta     → search by name
 * GET /api/products?category=X → filter by category
 * GET /api/categories          → use /api/products/categories instead
 */

import { NextRequest, NextResponse } from 'next/server';
import { getProductsFromDB } from '@/lib/products';

export const revalidate = 0; // always fresh

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const q = searchParams.get('q') ?? undefined;
    const category = searchParams.get('category') ?? undefined;

    const products = await getProductsFromDB({ q, category });
    return NextResponse.json(products);
  } catch (err) {
    console.error('[/api/products] error:', err);
    return NextResponse.json({ error: 'Failed to fetch products' }, { status: 500 });
  }
}
