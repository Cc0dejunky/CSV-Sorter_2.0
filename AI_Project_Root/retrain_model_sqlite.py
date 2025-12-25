"""Offline retraining script for SQLite-based feedback table.

This script trains a lightweight text classifier (Tfidf + LogisticRegression)
that maps raw text to corrected/normalized text labels. It saves the resulting
pipeline as `normalization_model.joblib` (or path from env var).

It is intentionally light-weight so it can run quickly on-device.
"""
import os
try:
    import joblib
except Exception:
    try:
        from sklearn.externals import joblib  # fallback
    except Exception:
        joblib = None
from db_adapter import get_connection

from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


MODEL_PATH = os.getenv("NORMALIZATION_MODEL_PATH", "normalization_model.joblib")
MIN_PAIRS = int(os.getenv("MIN_TRAINING_PAIRS", "5"))


def retrain():
    print("Starting offline retrain (SQLite)...")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT p.text_content, f.correction FROM feedback f JOIN products p ON p.id = f.product_id WHERE f.correction IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    pairs = [(r[0], r[1]) for r in rows if r[1] and r[0]]

    if len(pairs) < MIN_PAIRS:
        print(f"Not enough training pairs ({len(pairs)}) found. Need at least {MIN_PAIRS} to retrain.")
        return False

    X = [p[0] for p in pairs]
    y = [p[1] for p in pairs]

    print(f"Training normalization classifier on {len(X)} pairs...")
    clf = make_pipeline(TfidfVectorizer(ngram_range=(1,2), max_features=20000), LogisticRegression(max_iter=1000))
    clf.fit(X, y)

    # Save model
    try:
        joblib.dump(clf, MODEL_PATH)
        print(f"Saved new normalization model to {MODEL_PATH}")
    except Exception as e:
        print(f"Failed to save model: {e}")
        return False

    # Optionally upload to R2 as backup
    if os.getenv("R2_BUCKET_NAME"):
        try:
            import boto3
            s3 = boto3.client(
                's3',
                endpoint_url=os.getenv("R2_ENDPOINT_URL"),
                aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
            )
            s3.upload_file(MODEL_PATH, os.getenv("R2_BUCKET_NAME"), f"models/{os.path.basename(MODEL_PATH)}")
            print(f"Backed up model to R2 bucket {os.getenv('R2_BUCKET_NAME')}")
        except Exception as e:
            print(f"Failed to upload model to R2: {e}")

    return True


if __name__ == "__main__":
    retrain()
