import os
import joblib
from db_adapter import get_connection, ensure_tables
from AI_Project_Root.retrain_model_sqlite import retrain


def setup_feedback_pairs():
    ensure_tables()
    conn = get_connection()
    cur = conn.cursor()
    # Clear tables
    cur.execute("DELETE FROM feedback")
    cur.execute("DELETE FROM products")
    # Insert sample products and feedback
    examples = [
        ("Nvy Blue T-shirt", "Navy Blue T-shirt"),
        ("Rd Shirt", "Red Shirt"),
        ("Greenish Pants", "Green Pants"),
        ("Blk Jacket", "Black Jacket"),
        ("White Sneaks", "White Sneakers")
    ]
    for raw, corr in examples:
        cur.execute("INSERT INTO products (text_content, normalized_value, needs_review, confidence) VALUES (?, ?, ?, ?)", (raw, None, 1, 0.0))
        pid = cur.lastrowid
        cur.execute("INSERT INTO feedback (product_id, is_approved, correction) VALUES (?, ?, ?)", (pid, 0, corr))
    conn.commit()
    cur.close()
    conn.close()


def test_retrain_creates_model(tmp_path):
    # prepare db
    setup_feedback_pairs()
    # ensure old model removed
    model_path = os.getenv("NORMALIZATION_MODEL_PATH", "normalization_model.joblib")
    if os.path.exists(model_path):
        os.remove(model_path)

    ok = retrain()
    assert ok is True
    assert os.path.exists(model_path)

    # load and test prediction
    clf = joblib.load(model_path)
    pred = clf.predict(["Rd Shirt"])[0]
    assert pred == "Red Shirt"
