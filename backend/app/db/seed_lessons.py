"""
Τρέξε αυτό ΜΕΤΑ που ανέβει ο server για να γεμίσεις τη βάση με αρχικά μαθήματα.

Χρήση:
    python seed_lessons.py
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

# (topic, age_group, order_index)
LESSONS_TO_SEED = [
    # JUNIOR (8-11)
    ("Τι είναι τα χρήματα;",               "junior",       1),
    ("Ανάγκες vs Επιθυμίες",               "junior",       2),
    ("Πώς να αποταμιεύεις στον κουμπαρά",  "junior",       3),
    ("Τιμές και αξία αντικειμένων",        "junior",       4),

    # INTERMEDIATE (12-14)
    ("Τι είναι ο προϋπολογισμός (budget);", "intermediate", 1),
    ("Αποταμίευση και στόχοι",              "intermediate", 2),
    ("Τι είναι ο τόκος;",                  "intermediate", 3),
    ("Έσοδα και Έξοδα",                    "intermediate", 4),

    # SENIOR (15-17)
    ("Πώς λειτουργεί η τράπεζα;",          "senior",       1),
    ("Βασικές αρχές επενδύσεων",           "senior",       2),
    ("Πιστωτικό σκορ και δάνεια",          "senior",       3),
    ("Φορολογία — τα βασικά",              "senior",       4),
]


async def seed():
    async with httpx.AsyncClient(timeout=60) as client:
        for topic, age_group, order_index in LESSONS_TO_SEED:
            print(f"⏳ Generating: [{age_group}] {topic}")
            r = await client.post(
                f"{BASE_URL}/lessons/generate",
                params={"topic": topic, "age_group_str": age_group, "order_index": order_index},
            )
            if r.status_code == 201:
                data = r.json()
                print(f"  ✅ lesson_id={data['lesson_id']}")
            else:
                print(f"  ❌ Error: {r.text}")


if __name__ == "__main__":
    asyncio.run(seed())