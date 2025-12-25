"""Demo: seed feedback, retrain offline and reload model into memory (for quick local verification).

Usage: python scripts/demo_retrain_and_reload.py
"""
from db_adapter import get_connection, ensure_tables
from AI_Project_Root.retrain_model_sqlite import retrain
import os

ensure_tables()
conn = get_connection(); cur = conn.cursor()
# Insert a small set of correction pairs (idempotent)
pairs = [
    ("Rd Shirt", "Red Shirt"),
    ("Nvy Blue T-shirt", "Navy Blue T-shirt"),
    ("Blk Jacket", "Black Jacket"),
    ("White Sneaks", "White Sneakers"),
    ("Greenish Pants", "Green Pants")
]
for raw, corr in pairs:
    cur.execute("INSERT INTO products (text_content, normalized_value, needs_review, confidence) VALUES (?, ?, ?, ?)", (raw, None, 1, 0.0))
    pid = cur.lastrowid
    cur.execute("INSERT INTO feedback (product_id, is_approved, correction) VALUES (?, ?, ?)", (pid, 0, corr))
conn.commit(); cur.close(); conn.close()
print("Seeded feedback pairs.")
ok = retrain()
print("Retrain finished:", ok)
# Reload model into memory
import main
ok2 = main.load_model()
print("Model loaded into server process:", ok2)
if ok2 and main.normalization_model is not None:
    try:
        print("Sample prediction:", main.normalization_model.predict(["Rd Shirt"]))
    except Exception as e:
        print("Prediction failed:", e)
else:
    print("No model available to test predictions.")
