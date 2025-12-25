"""Seed the taxonomy_reference table from a Google Product Taxonomy file or URL.

Usage:
  python AI_Project_Root/seed_taxonomy.py --file path/to/taxonomy.txt
  python AI_Project_Root/seed_taxonomy.py --url https://www.../taxonomy.txt

If no path/URL is provided, the script inserts a small default subset to get started.
"""
import argparse
import csv
import requests
from db_adapter import get_connection, ensure_tables

DEFAULT_TAXONOMY = [
    ("1", "Animals & Pet Supplies > Pet Supplies > Dog Food"),
    ("2", "Apparel & Accessories > Clothing > Shirts & Tops"),
    ("3", "Apparel & Accessories > Clothing > Pants"),
    ("4", "Apparel & Accessories > Accessories > Jewelry"),
    ("5", "Home & Garden > Kitchen & Dining > Cookware")
]


def parse_lines(lines):
    pairs = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        # Google taxonomy lines are often: "1666	Animals & Pet Supplies > Pet Supplies > Dog Food"
        if "\t" in ln:
            tid, path = ln.split("\t", 1)
        elif "," in ln and ln.split(",",1)[0].strip().isdigit():
            tid, path = ln.split(",",1)
            tid = tid.strip()
            path = path.strip()
        else:
            # fallback: full line -> use numeric prefix if present
            parts = ln.split(' ', 1)
            if parts[0].isdigit() and len(parts) > 1:
                tid = parts[0]
                path = parts[1]
            else:
                tid = None
                path = ln
        label = path.split('>')[-1].strip() if '>' in path else path.strip()
        pairs.append((tid, path.strip(), label))
    return pairs


def seed_from_iter(lines):
    ensure_tables()
    conn = get_connection()
    cur = conn.cursor()
    pairs = parse_lines(lines)
    inserted = 0
    for tid, path, label in pairs:
        try:
            cur.execute("INSERT INTO taxonomy_reference (taxonomy_id, taxonomy_path, label) VALUES (?, ?, ?)", (tid, path, label))
            inserted += 1
        except Exception:
            # ignore duplicates or insertion errors
            continue
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {inserted} taxonomy rows")
    return inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to taxonomy text file")
    parser.add_argument("--url", help="URL to fetch taxonomy file from")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        seed_from_iter(lines)
    elif args.url:
        r = requests.get(args.url, timeout=10)
        r.raise_for_status()
        lines = r.text.splitlines()
        seed_from_iter(lines)
    else:
        # fallback small seed
        print("No file or URL provided; inserting small default taxonomy subset")
        seed_from_iter([f"{tid}\t{path}" for tid, path in DEFAULT_TAXONOMY])


if __name__ == "__main__":
    main()
