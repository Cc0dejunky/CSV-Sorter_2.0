import os
import sqlite3

DB_URL = os.getenv("DB_URL", "sqlite:///./dev.db")
path = DB_URL.split("sqlite:///")[-1]

with open("migrations/001_init.sql", "r") as f:
    sql = f.read()

conn = sqlite3.connect(path)
cur = conn.cursor()
cur.executescript(sql)
conn.commit()
cur.close()
conn.close()
print("Applied migrations to", path)
