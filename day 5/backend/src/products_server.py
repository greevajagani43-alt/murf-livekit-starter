"""
products_server.py
──────────────────
Lightweight FastAPI HTTP server that exposes product catalogue over HTTP
so the Next.js frontend can fetch real data from the same SQLite DB.

Run alongside the LiveKit agent:
    uvicorn products_server:app --host 0.0.0.0 --port 8001 --reload

Or add to your Taskfile / start script.

Endpoints:
    GET  /products                → all products
    GET  /products?category=X    → filtered by category
    GET  /products?q=atta        → name search
    GET  /categories             → distinct category list
    GET  /health                 → liveness probe
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from database_products import (
    init_products_db,
    get_all_products,
    get_products_by_category,
    search_products,
    get_categories,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Gate-check: seed DB if empty
    init_products_db()
    yield


app = FastAPI(title="Ratan Kirana Products API", lifespan=lifespan)

# Allow Next.js dev server (localhost:3000) and prod origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/categories")
def categories():
    return get_categories()


@app.get("/products")
def products(
    q: Optional[str] = Query(None, description="Name search query"),
    category: Optional[str] = Query(None, description="Exact category name"),
):
    if category:
        results = get_products_by_category(category)
        if q:
            q_lower = q.strip().lower()
            results = [r for r in results if q_lower in r["name"].lower()]
    elif q:
        results = search_products(q)
    else:
        results = get_all_products()
    return results
