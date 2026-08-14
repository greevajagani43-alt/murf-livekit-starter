"""
products_db.py
──────────────
Product catalogue for Ratan Kirana Store (Local Commerce Track).
Provides lookup tools for product availability, pricing, and details.
"""

from typing import Any, Dict, List, Optional

PRODUCTS_CATALOGUE = [
    {
        "id": "p1",
        "name": "Wireless Headphones",
        "category": "Electronics",
        "price": 1499,
        "unit": "1 piece",
        "in_stock": True,
        "stock_qty": 15,
        "description": "High bass Bluetooth wireless headphones with 20h battery life.",
    },
    {
        "id": "p2",
        "name": "Aashirvaad Shuddh Chakki Atta",
        "category": "Groceries",
        "price": 380,
        "unit": "10 kg",
        "in_stock": True,
        "stock_qty": 50,
        "description": "100% pure whole wheat flour.",
    },
    {
        "id": "p3",
        "name": "Fortune Sunlite Sunflower Oil",
        "category": "Groceries",
        "price": 165,
        "unit": "1 L pouch",
        "in_stock": True,
        "stock_qty": 30,
        "description": "Light and healthy refined sunflower oil.",
    },
    {
        "id": "p4",
        "name": "Amul Taaza Toned Milk",
        "category": "Dairy",
        "price": 27,
        "unit": "500 ml",
        "in_stock": True,
        "stock_qty": 100,
        "description": "Fresh pasteurized toned milk.",
    },
    {
        "id": "p5",
        "name": "Tata Salt Vacuum Evaporated",
        "category": "Groceries",
        "price": 28,
        "unit": "1 kg",
        "in_stock": True,
        "stock_qty": 80,
        "description": "Iodized crystal salt.",
    },
    {
        "id": "p6",
        "name": "India Gate Basmati Rice Feast",
        "category": "Groceries",
        "price": 450,
        "unit": "5 kg",
        "in_stock": True,
        "stock_qty": 20,
        "description": "Long grain aromatic basmati rice.",
    },
    {
        "id": "p7",
        "name": "Tata Sampann Toor Dal",
        "category": "Groceries",
        "price": 160,
        "unit": "1 kg",
        "in_stock": False,
        "stock_qty": 0,
        "description": "Unpolished protein-rich arhar dal.",
    },
]


def search_products(query: str) -> List[Dict[str, Any]]:
    """Search catalogue by keyword."""
    q = query.lower().strip()
    return [
        p for p in PRODUCTS_CATALOGUE
        if q in p["name"].lower() or q in p["category"].lower() or q in p["description"].lower()
    ]


def get_product_by_id(prod_id: str) -> Optional[Dict[str, Any]]:
    """Find product by ID."""
    for p in PRODUCTS_CATALOGUE:
        if p["id"].lower() == prod_id.lower():
            return p
    return None
