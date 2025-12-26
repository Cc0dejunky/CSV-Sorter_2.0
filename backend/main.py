# ANCHOR: Product Command Center Brain
# LOCATION: /backend/main.py
# UX_RULE: Must process /submit-feedback instantly for 160wpm typing.
# BRAND: Provides data for Neon Pink/Aqua UI.

import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from db_adapter import get_connection, ensure_tables

app = FastAPI()
ensure_tables()

# THE HANDSHAKE: Unlocks Port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Feedback(BaseModel):
    product_id: int
    is_approved: bool
    correction: Optional[str] = None

@app.get("/products")
def get_products():
    """Gallery View: Pulls all products for the Tech-White dashboard."""
    conn = get_connection()
    cur = conn.cursor()
    # Pulling every column to ensure prices/images show up
    cur.execute("SELECT * FROM products ORDER BY created_at DESC")
    rows = cur.fetchall()
    
    colnames = [d[0] for d in cur.description]
    results = []
    for r in rows:
        d = dict(zip(colnames, r))
        # Ensure image and price fields are named correctly for the frontend
        results.append({
            "id": d.get("id"),
            "text_content": d.get("text_content"),
            "price": d.get("Variant Price") or d.get("price") or "0.00",
            "variant_image": d.get("Variant Image") or d.get("variant_image") or ""
        })
    cur.close()
    conn.close()
    return results

@app.post("/submit-feedback")
def submit_feedback(fb: Feedback):
    """160wpm Trigger: Updates SQLite immediately on Enter key."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE products SET text_content = ?, needs_review = 0 WHERE id = ?", 
                (fb.correction, fb.product_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}