import os
import csv
import io
import boto3
import joblib
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from db_adapter import get_connection, ensure_tables

app = FastAPI()

# Ensure local DB schema exists (SQLite for local testing)
ensure_tables()


import difflib


def vocabulary_lookup(raw_text: str):
    """Look up direct vocabulary mappings. Returns (normalized, confidence, source) or (None, 0.0, None)."""
    if not raw_text:
        return None, 0.0, None
    conn = get_connection()
    cur = conn.cursor()
    try:
        s = raw_text.strip()
        lower = s.lower()
        # Exact (whole string) match
        cur.execute("SELECT normalized, category FROM vocabulary WHERE token = ?", (lower,))
        row = cur.fetchone()
        if row and row[0]:
            return row[0], 1.0, row[1] or 'vocab'
        # Token-level mapping (replace tokens that have a mapping)
        tokens = lower.split()
        mapped = []
        any_mapped = False
        categories = set()
        for t in tokens:
            cur.execute("SELECT normalized, category FROM vocabulary WHERE token = ?", (t,))
            r = cur.fetchone()
            if r and r[0]:
                mapped.append(r[0])
                any_mapped = True
                if r[1]:
                    categories.add(r[1])
            else:
                mapped.append(t)
        if any_mapped:
            cat = ",".join(sorted(categories)) if categories else 'vocab'
            return " ".join(mapped), 1.0, cat
        return None, 0.0, None
    finally:
        cur.close()
        conn.close()


def taxonomy_search(raw_text: str, threshold: float = 0.7):
    """Do a lightweight semantic search over taxonomy_reference using difflib.
    Returns (taxonomy_label_or_path, confidence) or (None, 0.0).
    """
    if not raw_text:
        return None, 0.0
    conn = get_connection()
    cur = conn.cursor()
    try:
        lower = raw_text.strip().lower()
        cur.execute("SELECT taxonomy_path, label FROM taxonomy_reference")
        candidates = cur.fetchall()
        best = None
        best_score = 0.0
        for row in candidates:
            path = (row[0] or '')
            label = (row[1] or '')
            # check label first
            score_label = difflib.SequenceMatcher(None, lower, label.lower()).ratio() if label else 0.0
            score_path = difflib.SequenceMatcher(None, lower, path.lower()).ratio() if path else 0.0
            score = max(score_label, score_path)
            if score > best_score:
                best_score = score
                best = label if score_label >= score_path else path
        if best and best_score >= threshold:
            # confidence tuned slightly below exact vocab
            return best, round(best_score, 2)
        return None, 0.0
    finally:
        cur.close()
        conn.close()

# Model holder
normalization_model = None
model_has_proba = False
MODEL_PATH = os.getenv("NORMALIZATION_MODEL_PATH", "normalization_model.joblib")
THRESHOLD_CONFIDENCE = float(os.getenv("NORMALIZATION_CONFIDENCE_THRESHOLD", "0.9"))


def load_model():
    global normalization_model, model_has_proba
    if os.path.exists(MODEL_PATH):
        try:
            normalization_model = joblib.load(MODEL_PATH)
            model_has_proba = hasattr(normalization_model, "predict_proba")
            print(f"Loaded normalization model from {MODEL_PATH}. has_proba={model_has_proba}")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            normalization_model = None
            model_has_proba = False
            return False
    else:
        print("No normalization_model.joblib found; starting without a model")
        normalization_model = None
        model_has_proba = False
        return False

# Try load at startup
load_model()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic model for receiving feedback
class Feedback(BaseModel):
    product_id: int
    is_approved: bool
    correction: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "CSV-Sorter API is running"}

@app.get("/products-for-review")
def get_products_for_review():
    """Return products that need human review (SQLite implementation)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, text_content, normalized_value, confidence FROM products WHERE needs_review = 1 ORDER BY created_at ASC LIMIT 50")
    rows = cur.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "text": r[1],
            "normalized": r[2],
            "confidence": round(r[3] or 0.0, 2)
        })
    cur.close()
    conn.close()
    return results


@app.get("/get_products_for_review")
def get_products_for_review_alias():
    """Alias endpoint matching original plan name."""
    return get_products_for_review()


@app.get("/products")
def get_products(all: bool = False):
    """Return products from the DB.
    If `all` is false (default) return items where `needs_review = 1` for human review.
    If `all` is true, return all products.
    This will return every column present in the `products` table so the frontend can consume Shopify-like fields when present.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Get column names so we can return complete objects even if schema evolves
    cur.execute("PRAGMA table_info(products)")
    cols = [r[1] for r in cur.fetchall()]

    if all:
        cur.execute("SELECT * FROM products ORDER BY created_at DESC")
    else:
        cur.execute("SELECT * FROM products WHERE needs_review = 1 ORDER BY created_at ASC")

    rows = cur.fetchall()
    results = []
    for r in rows:
        results.append({cols[i]: r[i] for i in range(len(cols))})

    cur.close()
    conn.close()
    return results

@app.post("/submit-feedback")
def submit_feedback(feedback: Feedback):
    """Store human feedback and clear needs_review flag."""
    conn = get_connection()
    cur = conn.cursor()
    # Insert feedback
    cur.execute("INSERT INTO feedback (product_id, is_approved, correction) VALUES (?, ?, ?)",
                (feedback.product_id, int(feedback.is_approved), feedback.correction))
    # Update product: set needs_review false and update normalized value if correction provided
    if feedback.correction:
        cur.execute("UPDATE products SET normalized_value = ?, needs_review = 0 WHERE id = ?",
                    (feedback.correction, feedback.product_id))
    else:
        cur.execute("UPDATE products SET needs_review = 0 WHERE id = ?", (feedback.product_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV, run initial normalization (joblib) if available, and mark items for review as needed."""
    content = await file.read()
    decoded = content.decode('utf-8')

    # Archive to Cloudflare R2 (if configured)
    if os.getenv("R2_BUCKET_NAME"):
        try:
            s3 = boto3.client(
                's3',
                endpoint_url=os.getenv("R2_ENDPOINT_URL"),
                aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
            )
            s3.put_object(Bucket=os.getenv("R2_BUCKET_NAME"), Key=f"raw_uploads/{file.filename}", Body=content)
            print(f"Archived {file.filename} to R2")
        except Exception as e:
            print(f"Failed to upload to R2: {e}")

    csv_reader = csv.reader(io.StringIO(decoded))
    conn = get_connection()
    cur = conn.cursor()

    # Skip header
    next(csv_reader, None)

    count = 0
    for row in csv_reader:
        if row:
            raw = row[0]
            normalized = None
            confidence = 0.0
            needs_review = 1

            # WATERFALL: 1) vocabulary, 2) taxonomy semantic search, 3) ML model
            # 1) vocabulary
            try:
                voc_norm, voc_conf, voc_cat = vocabulary_lookup(raw)
                if voc_norm:
                    normalized = voc_norm
                    confidence = voc_conf
                    needs_review = 0
                else:
                    # 2) taxonomy semantic search
                    tax_norm, tax_score = taxonomy_search(raw)
                    if tax_norm:
                        normalized = tax_norm
                        # map tax_score (0-1) to confidence with a boost
                        confidence = round(max(tax_score, 0.85), 2)
                        if confidence >= THRESHOLD_CONFIDENCE:
                            needs_review = 0
                    else:
                        # 3) fallback to ML model
                        if normalization_model is not None:
                            try:
                                normalized = normalization_model.predict([raw])[0]
                                # If model supports predict_proba, compute confidence
                                if model_has_proba:
                                    probs = normalization_model.predict_proba([raw])[0]
                                    confidence = float(max(probs))
                                else:
                                    confidence = 0.0
                                # Auto-approve if confidence meets threshold
                                if confidence >= THRESHOLD_CONFIDENCE:
                                    needs_review = 0
                            except Exception as e:
                                print(f"Model prediction failed for '{raw}': {e}")
                                normalized = None
                                confidence = 0.0
                                needs_review = 1
            except Exception as e:
                print(f"Waterfall prediction failed for '{raw}': {e}")
                normalized = None
                confidence = 0.0
                needs_review = 1

            cur.execute("INSERT INTO products (text_content, normalized_value, needs_review, confidence) VALUES (?, ?, ?, ?)",
                        (raw, normalized, needs_review, confidence))
            count += 1

    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Successfully uploaded {count} products"}

@app.post("/trigger-retrain")
async def trigger_retrain(background_tasks: BackgroundTasks):
    """Trigger a retrain in the background. Chooses SQLite offline retrain when DB_URL indicates sqlite."""
    db_url = os.getenv("DB_URL", "sqlite")
    if "sqlite" in db_url:
        from AI_Project_Root.retrain_model_sqlite import retrain as sqlite_retrain
        background_tasks.add_task(sqlite_retrain)
    else:
        try:
            from AI_Project_Root.retrain_model import retrain as pg_retrain
            background_tasks.add_task(pg_retrain)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrain import failed: {e}")
    return {"message": "Retraining started in background"}


@app.post("/reload_model")
def reload_model():
    """Reload the normalization joblib model at runtime."""
    ok = load_model()
    if ok:
        return {"status": "reloaded"}
    else:
        raise HTTPException(status_code=500, detail="Failed to load model")