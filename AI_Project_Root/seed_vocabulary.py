"""Seed the vocabulary table with common abbreviations and allow loading from CSV.

CSV format: token,normalized
Example row: nvy,Navy
"""
import argparse
import csv
from db_adapter import get_connection, ensure_tables

# Default small vocabulary mapping
DEFAULT_VOCAB = [
    ("wmns", "Women's"),
    ("womens", "Women's"),
    ("nvy", "Navy"),
    ("nv", "Navy"),
    ("rd", "Red"),
    ("blk", "Black"),
    ("oz", "Ounce"),
    ("l", "Liter"),
    ("ml", "Milliliter"),
    ("sml", "Small"),
    ("med", "Medium"),
    ("lg", "Large")
]


def seed_from_iter(pairs, source=None):
    ensure_tables()
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    for token, normalized in pairs:
        token_norm = token.strip().lower()
        try:
            cur.execute("INSERT OR REPLACE INTO vocabulary (token, normalized, source) VALUES (?, ?, ?)", (token_norm, normalized.strip(), source))
            inserted += 1
        except Exception:
            continue
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted/updated {inserted} vocabulary rows")
    return inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="CSV file with token,normalized columns")
    args = parser.parse_args()

    if args.file:
        pairs = []
        with open(args.file, "r", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row:
                    continue
                token = row[0]
                norm = row[1] if len(row) > 1 else ''
                pairs.append((token, norm))
        seed_from_iter(pairs, source=args.file)
    else:
        print("No file given; inserting default vocabulary list")
        seed_from_iter(DEFAULT_VOCAB, source="default")


if __name__ == "__main__":
    main()
