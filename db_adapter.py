import os
import sqlite3
from urllib.parse import urlparse

# Persist DB to /workspaces/persistent by default so it survives container restarts
DEFAULT_PERSIST_DIR = os.getenv("WORKSPACE_PERSIST_DIR", "/workspaces/persistent")
if not os.path.exists(DEFAULT_PERSIST_DIR):
    try:
        os.makedirs(DEFAULT_PERSIST_DIR, exist_ok=True)
    except Exception:
        pass
DB_URL = os.getenv("DB_URL", f"sqlite:///{os.path.join(DEFAULT_PERSIST_DIR, 'dev.db')}")

def is_sqlite():
    return DB_URL.startswith("sqlite")

def get_connection():
    """Return a DB connection object. For sqlite, return sqlite3.Connection."""
    if is_sqlite():
        # sqlite:///./dev.db or sqlite:///dev.db accepted
        path = DB_URL.split("sqlite:///")[-1]
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        # Placeholder for Postgres in future (psycopg2)
        raise RuntimeError("Only sqlite is supported by db_adapter in this branch")

def ensure_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_content TEXT NOT NULL,
        normalized_value TEXT,
        needs_review INTEGER DEFAULT 1,
        confidence REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        is_approved INTEGER NOT NULL,
        correction TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        vector_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    # Taxonomy reference table for Google Product Taxonomy (or similar)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS taxonomy_reference (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        taxonomy_id TEXT,
        taxonomy_path TEXT NOT NULL,
        label TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Vocabulary table for direct token/abbreviation -> normalized mapping
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        normalized TEXT NOT NULL,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Ensure we have a 'category' column (add if missing)
    cur.execute("PRAGMA table_info(vocabulary)")
    cols = [row[1] for row in cur.fetchall()]
    if 'category' not in cols:
        try:
            cur.execute("ALTER TABLE vocabulary ADD COLUMN category TEXT")
        except Exception:
            # sqlite may raise if the column already exists due to race; ignore
            pass

    conn.commit()
    cur.close()
    conn.close()
