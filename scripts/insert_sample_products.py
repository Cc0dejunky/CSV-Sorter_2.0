import os
import sqlite3

DB_URL = os.getenv("DB_URL", "sqlite:///./dev.db")
path = DB_URL.split("sqlite:///")[-1]
conn = sqlite3.connect(path)
cur = conn.cursor()

samples = [
    ("Nvy Blue T-shirt",),
    ("Rd Shirt",),
    ("Greenish Pants",)
]
cur.executemany("INSERT INTO products (text_content, needs_review) VALUES (?, 1)", samples)
conn.commit()
print(f"Inserted {len(samples)} sample products")
cur.close()
conn.close()
