"""Seed a small vocabulary table with common abbreviations and normalizations.

Usage:
    python scripts/seed_vocabulary.py

This inserts tokens like: 'wmns' -> "Women's", 'nvy' -> 'Navy', 'oz' -> 'Ounce'.
"""
from db_adapter import get_connection, ensure_tables

DEFAULT_PAIRS = [
    ("sm", "Small", "Size"), ("sml", "Small", "Size"),
    ("md", "Medium", "Size"), ("med", "Medium", "Size"),
    ("lg", "Large", "Size"), ("lrg", "Large", "Size"),
    ("xl", "Extra Large", "Size"), ("xxl", "2XL", "Size"),
    ("os", "One Size", "Size"), ("osfa", "One Size Fits All", "Size"),

    ("nvy", "Navy", "Color"), ("blk", "Black", "Color"),
    ("wht", "White", "Color"), ("grn", "Green", "Color"),
    ("gry", "Gray", "Color"), ("slvr", "Silver", "Color"),
    ("multi", "Multicolor", "Color"),

    ("wmns", "Women's", "Gender"), ("mens", "Men's", "Gender"),
    ("s/s", "Short Sleeve", "Feature"), ("l/s", "Long Sleeve", "Feature"),
    ("ctn", "Cotton", "Material"), ("poly", "Polyester", "Material"),
    ("btn", "Button", "Feature"), ("v-neck", "V-Neck", "Feature"),

    ("oz", "Ounce", "Unit"), ("fl oz", "Fluid Ounce", "Unit"),
    ("ml", "Milliliter", "Unit"), ("lb", "Pound", "Unit"),
    ("kg", "Kilogram", "Unit"), ("ea", "Each", "Quantity"),
    ("pk", "Pack", "Quantity"), ("pkg", "Package", "Quantity"),

    # additional small mappings kept (lower risk)
    ("womens", "Women's", "Gender"), ("rd", "Red", "Color"),
    ("sneaks", "Sneakers", "Product"), ("l", "Large", "Size"), ("m", "Medium", "Size"), ("s", "Small", "Size")
]


def seed(pairs=DEFAULT_PAIRS):
    ensure_tables()
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    for token, norm, category in pairs:
        try:
            cur.execute(
                "INSERT OR IGNORE INTO vocabulary (token, normalized, source, category) VALUES (?, ?, ?, ?)",
                (token.lower(), norm, 'seed', category)
            )
            inserted += 1
        except Exception as e:
            print(f"Failed insert {token}: {e}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"Seeded {inserted} vocabulary items")


if __name__ == "__main__":
    seed()