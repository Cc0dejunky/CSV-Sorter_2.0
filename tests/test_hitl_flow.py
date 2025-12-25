from fastapi.testclient import TestClient
import os
import tempfile
import json

from main import app
from db_adapter import ensure_tables, get_connection

client = TestClient(app)


def setup_module(module):
    # Ensure migrations and clean DB for test
    os.environ["DB_URL"] = "sqlite:///./test_dev.db"
    ensure_tables()
    # Clean tables
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM feedback")
    cur.execute("DELETE FROM products")
    conn.commit()
    cur.close()
    conn.close()


def test_upload_and_get_review():
    # Prepare a tiny CSV
    csv_data = "text\nSample Product A\n"
    files = {"file": ("sample.csv", csv_data, "text/csv")}
    resp = client.post("/upload-csv", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "Successfully uploaded" in data["message"]

    # Now fetch products for review
    resp = client.get("/products-for-review")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1


def teardown_module(module):
    # Clean up test DB
    try:
        os.remove("test_dev.db")
    except FileNotFoundError:
        pass
