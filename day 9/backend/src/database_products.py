"""
database_products.py
────────────────────
SQLite product catalogue for Ratan Kirana & General Store.

Gate-check: if the `products` table doesn't exist (or is empty), seeds it
from SEED_DATA automatically. The DB file lives at data/kirana_products.db
relative to this file's directory so backend + frontend share the same path.

Public API
──────────
    init_products_db()          → call once at startup
    get_all_products()          → list[dict]
    get_products_by_category(c) → list[dict]
    search_products(query)      → list[dict]  (name LIKE match, case-insensitive)
    get_product_by_id(id)       → dict | None
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger("database_products")

# ── DB path ────────────────────────────────────────────────────────────────
# Resolves to  backend/data/kirana_products.db  regardless of cwd.
_DB_PATH = Path(__file__).parent.parent / "data" / "kirana_products.db"


def _get_conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ── Seed data ──────────────────────────────────────────────────────────────
# Mirrors data_seed.sql but adapted for SQLite (no SERIAL, uses INTEGER PRIMARY KEY).

SEED_DATA: list[tuple] = [
    # (name, size, price, icon, category, qty)
    # Atta & Flour
    ("Aashirvaad Atta", "5 kg", 295.00, "Wheat", "Atta & Flour", 18),
    ("Fortune Chakki Fresh Atta", "5 kg", 285.00, "Wheat", "Atta & Flour", 15),
    ("Besan", "500 g", 75.00, "Wheat", "Atta & Flour", 22),
    ("Maida", "500 g", 35.00, "Wheat", "Atta & Flour", 20),
    ("Sooji / Rava", "500 g", 40.00, "Wheat", "Atta & Flour", 25),
    # Rice & Dal
    ("India Gate Basmati Rice", "5 kg", 650.00, "Wheat", "Rice & Dal", 10),
    ("Daawat Basmati Rice", "5 kg", 620.00, "Wheat", "Rice & Dal", 12),
    ("Sona Masoori Rice", "5 kg", 350.00, "Wheat", "Rice & Dal", 14),
    ("Toor Dal", "1 kg", 180.00, "Wheat", "Rice & Dal", 25),
    ("Moong Dal", "1 kg", 145.00, "Wheat", "Rice & Dal", 20),
    ("Masoor Dal", "1 kg", 110.00, "Wheat", "Rice & Dal", 18),
    ("Chana Dal", "1 kg", 95.00, "Wheat", "Rice & Dal", 22),
    # Oil & Ghee
    ("Fortune Sunflower Oil", "1 L", 145.00, "Droplets", "Oil & Ghee", 30),
    ("Fortune Groundnut Oil", "1 L", 175.00, "Droplets", "Oil & Ghee", 24),
    ("Fortune Mustard Oil", "1 L", 160.00, "Droplets", "Oil & Ghee", 20),
    ("Amul Ghee", "1 L", 650.00, "Milk", "Oil & Ghee", 12),
    ("Patanjali Cow Ghee", "500 ml", 350.00, "Milk", "Oil & Ghee", 14),
    # Spices
    ("MDH Chana Masala", "100 g", 45.00, "Sprout", "Spices", 25),
    ("MDH Garam Masala", "100 g", 55.00, "Sprout", "Spices", 28),
    ("Everest Turmeric Powder", "100 g", 35.00, "Sprout", "Spices", 30),
    ("Everest Red Chilli Powder", "100 g", 40.00, "Flame", "Spices", 32),
    ("Everest Coriander Powder", "100 g", 38.00, "Sprout", "Spices", 25),
    ("Tata Salt", "1 kg", 28.00, "Waves", "Spices", 40),
    # Tea & Coffee
    ("Tata Tea Premium", "500 g", 280.00, "Coffee", "Tea & Coffee", 18),
    ("Red Label Tea", "500 g", 270.00, "Coffee", "Tea & Coffee", 16),
    ("Bru Instant Coffee", "100 g", 180.00, "Coffee", "Tea & Coffee", 14),
    ("Nescafe Classic", "100 g", 320.00, "Coffee", "Tea & Coffee", 12),
    # Sugar & Sweeteners
    ("Madhur Sugar", "1 kg", 48.00, "Candy", "Sugar & Sweeteners", 35),
    # Biscuits & Snacks
    ("Parle-G Biscuits", "800 g", 100.00, "Cookie", "Biscuits & Snacks", 30),
    ("Britannia Good Day", "200 g", 40.00, "Cookie", "Biscuits & Snacks", 28),
    ("Britannia Marie Gold", "250 g", 40.00, "Cookie", "Biscuits & Snacks", 30),
    ("Hide & Seek", "120 g", 40.00, "Cookie", "Biscuits & Snacks", 24),
    ("Lays Magic Masala", "52 g", 20.00, "Cookie", "Biscuits & Snacks", 45),
    ("Kurkure Masala Munch", "90 g", 20.00, "Cookie", "Biscuits & Snacks", 40),
    ("Haldiram Aloo Bhujia", "200 g", 70.00, "Cookie", "Biscuits & Snacks", 20),
    # Dairy
    ("Amul Taaza Milk", "1 L", 65.00, "Milk", "Dairy", 25),
    ("Amul Butter", "100 g", 60.00, "Milk", "Dairy", 18),
    ("Amul Cheese Slices", "200 g", 140.00, "Milk", "Dairy", 15),
    ("Amul Curd", "400 g", 40.00, "Milk", "Dairy", 20),
    # Beverages
    ("Coca-Cola", "750 ml", 45.00, "GlassWater", "Beverages", 25),
    ("Thums Up", "750 ml", 45.00, "GlassWater", "Beverages", 22),
    ("Sprite", "750 ml", 45.00, "GlassWater", "Beverages", 20),
    ("Real Mixed Fruit Juice", "1 L", 130.00, "GlassWater", "Beverages", 12),
    ("Frooti Mango Drink", "1 L", 70.00, "GlassWater", "Beverages", 18),
    # Personal Care
    ("Dove Bathing Soap", "100 g", 55.00, "Bath", "Personal Care", 30),
    ("Lux Soap", "100 g", 38.00, "Bath", "Personal Care", 35),
    ("Colgate Strong Teeth", "200 g", 110.00, "Smile", "Personal Care", 22),
    ("Clinic Plus Shampoo", "340 ml", 210.00, "Droplets", "Personal Care", 15),
    ("Parachute Coconut Oil", "200 ml", 95.00, "Droplets", "Personal Care", 20),
    # Household
    ("Surf Excel Matic", "2 kg", 390.00, "Sparkles", "Household", 12),
    ("Vim Dishwash Bar", "200 g", 25.00, "Sparkles", "Household", 30),
    ("Harpic Toilet Cleaner", "500 ml", 110.00, "SprayCan", "Household", 18),
    ("Dettol Liquid", "250 ml", 95.00, "ShieldCheck", "Household", 16),
]

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    size     TEXT    NOT NULL,
    price    REAL    NOT NULL,
    icon     TEXT    NOT NULL,
    category TEXT    NOT NULL,
    qty      INTEGER NOT NULL DEFAULT 0
);
"""


def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


# ── Public API ─────────────────────────────────────────────────────────────


def init_products_db() -> None:
    """Create the products table and seed it if empty. Safe to call multiple times."""
    with _get_conn() as conn:
        conn.execute(_CREATE_TABLE)
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            logger.info("Products table is empty — seeding %d rows…", len(SEED_DATA))
            conn.executemany(
                "INSERT INTO products (name, size, price, icon, category, qty) VALUES (?,?,?,?,?,?)",
                SEED_DATA,
            )
            logger.info("Seed complete.")
        else:
            logger.debug("Products DB already has %d rows — skipping seed.", count)


def get_all_products() -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    return [_row_to_dict(r) for r in rows]


def get_products_by_category(category: str) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE LOWER(category) = LOWER(?) ORDER BY name",
            (category,),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def search_products(query: str) -> list[dict]:
    """Case-insensitive partial search allowing multi-word matches across name and size."""
    words = query.strip().lower().split()
    if not words:
        return []

    with _get_conn() as conn:
        sql = "SELECT * FROM products WHERE "
        conditions = []
        params = []
        for word in words:
            conditions.append("LOWER(name || ' ' || REPLACE(size, ' ', '')) LIKE ?")
            params.append(f"%{word}%")

        sql += " AND ".join(conditions) + " ORDER BY name"
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_product_by_id(product_id: int) -> Optional[dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    return _row_to_dict(row) if row else None


def get_categories() -> list[str]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM products ORDER BY category"
        ).fetchall()
    return [r[0] for r in rows]


def get_product_stock(product_name: str) -> list[dict]:
    """Return full product info (name, size, price, qty) for stock validation.

    Returns a list of matching product dictionaries (usually 0 or 1 result).
    Uses LIKE for partial matching so "maida" matches "Maida".
    """
    pattern = f"%{product_name.strip()}%"
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?) ORDER BY name",
            (pattern,),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]
