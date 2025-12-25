"""Seed taxonomy_reference table from Google Product Taxonomy.

Usage:
  python scripts/seed_taxonomy.py --url <taxonomy_url>

Defaults to Google's canonical taxonomy file when available.
"""
import argparse
import requests
from db_adapter import get_connection, ensure_tables

DEFAULT_URL = "https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt"


def parse_and_insert(lines):
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Some files have `id\tpath` others are just path lines; handle both
        if '\t' in line:
            taxonomy_id, path = line.split('\t', 1)
        else:
            # No id available; use line index or empty id
            taxonomy_id = None
            path = line
        label = path.split('>')[-1].strip() if '>' in path else path.split('/')[-1].strip()
        try:
            cur.execute("INSERT INTO taxonomy_reference (taxonomy_id, taxonomy_path, label) VALUES (?, ?, ?)",
                        (taxonomy_id, path, label))
            inserted += 1
        except Exception:
            # ignore duplicates or errors
            pass
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {inserted} taxonomy rows")
    return inserted


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL, help="URL or local path to taxonomy file")
    parser.add_argument("--local", action="store_true", help="Treat --url as a local file path")
    args = parser.parse_args()

    ensure_tables()

    data = None
    if args.local:
        with open(args.url, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        parse_and_insert(lines)
    else:
        try:
            resp = requests.get(args.url, timeout=10)
            resp.raise_for_status()
            content = resp.text
            parse_and_insert(content.splitlines())
        except Exception as e:
            print(f"Failed to fetch taxonomy from {args.url}: {e}")
            print("You can download manually and run with --local <file>")