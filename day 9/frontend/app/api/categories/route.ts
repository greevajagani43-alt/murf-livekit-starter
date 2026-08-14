/**
 * app/api/categories/route.ts
 * ───────────────────────────
 * Returns the distinct product categories for the catalogue UI.
 */

import { NextResponse } from 'next/server';
import { getCategoriesFromDB } from '@/lib/products';

export const revalidate = 0; // always fresh

export async function GET() {
  try {
    const categories = await getCategoriesFromDB();
    return NextResponse.json(categories);
  } catch (err) {
    console.error('[/api/categories] error:', err);
    return NextResponse.json({ error: 'Failed to fetch categories' }, { status: 500 });
  }
}
