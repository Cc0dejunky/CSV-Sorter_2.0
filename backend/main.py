import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from db_adapter import get_connection, ensure_tables

app = FastAPI()
ensure_tables()

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
    conn = get_connection()
    cur = conn.cursor()
    # Fetching pending items for the review queue
    cur.execute("SELECT id, text_content, status FROM products WHERE status = 'pending' LIMIT 50")
    rows = cur.fetchall()
    results = [{"id": r["id"], "text_content": r["text_content"], "status": r["status"]} for r in rows]
    cur.close()
    conn.close()
    return results

@app.post("/submit-feedback")
def submit_feedback(fb: Feedback):
    conn = get_connection()
    cur = conn.cursor()
    # Update the product status and save the correction
    cur.execute(
        "UPDATE products SET status = ?, normalized_value = ? WHERE id = ?",
        ('approved' if fb.is_approved else 'corrected', fb.correction, fb.product_id)
    )
    # Also record in the feedback table for the AI to learn later
    cur.execute(
        "INSERT INTO feedback (product_id, is_approved, correction) VALUES (?, ?, ?)",
        (fb.product_id, 1 if fb.is_approved else 0, fb.correction)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}