"""
seed_demo_user.py  —  Day 6: Seed a demo customer for outbound call testing
──────────────────────────────────────────────────────────────────────────────
Run this once before triggering a demo outbound call so Saathi can greet
the customer by name and mention their usual order.

Usage:
    uv run python src/seed_demo_user.py

This creates a user with user_id = "rahul" in data/users.db.
When you trigger the call with --name "Rahul", the room name will contain
"rahul" and the agent will look up this profile automatically.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_database, save_user

DEMO_USERS = [
    {
        "user_id": "rahul",
        "name": "Rahul Sharma",
        "facts": {
            "delivery_address": "42 Shivaji Nagar, Maninagar, Ahmedabad",
            "usual_quantity": "2 Aashirvaad Atta 5kg",
            "preferred_slot": "morning (9–11 AM)",
            "past_orders": [
                "2x Aashirvaad Atta 5kg, 1L Fortune Sunflower Oil",
                "2x Aashirvaad Atta 5kg, 500g Tata Tea",
            ],
        },
    },
    {
        "user_id": "priya",
        "name": "Priya Patel",
        "facts": {
            "delivery_address": "15 Gandhi Chowk, Maninagar, Ahmedabad",
            "usual_quantity": "1 Aashirvaad Atta 5kg, 1 Toor Dal 1kg",
            "preferred_slot": "evening (6–8 PM)",
            "past_orders": [
                "1x Aashirvaad Atta 5kg, 1kg Toor Dal",
            ],
        },
    },
]


def main():
    print("Initialising user database…")
    init_database()

    for user in DEMO_USERS:
        success = save_user(
            user_id=user["user_id"],
            name=user["name"],
            facts=user["facts"],
            language_preference="hi",
        )
        if success:
            print(f"  [OK] Seeded user: {user['name']} (user_id={user['user_id']!r})")
        else:
            print(f"  [FAIL] Failed to seed: {user['name']}")

    print("\nDone! You can now trigger a demo call:")
    print("  uv run python src/trigger_call.py --number +91XXXXXXXXXX --name Rahul")
    print("  --> Room name will contain 'rahul' and agent will greet Rahul Sharma.")


if __name__ == "__main__":
    main()
