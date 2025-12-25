"""Consolidate feedback from the SQLite DB into a simple CSV of training pairs.

Usage:
    python AI_Project_Root/Consolidate_feedback.py --out feedback_pairs.csv

This script reads the `feedback` table and writes rows of (original_text, correction)
for use by the offline retrain pipeline.
"""
import csv
import argparse
from db_adapter import get_connection


def consolidate(output_path="feedback_pairs.csv", min_count=1):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT p.text_content, f.correction FROM feedback f JOIN products p ON p.id = f.product_id WHERE f.correction IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Optionally group/unique; for now write all pairs
    if not rows:
        print("No correction rows found in feedback table.")
        return 0

    with open(output_path, "w", newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(["original", "correction"])
        for r in rows:
            writer.writerow([r[0], r[1]])

    print(f"Wrote {len(rows)} feedback pairs to {output_path}")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="feedback_pairs.csv")
    args = parser.parse_args()
    consolidate(args.out)
