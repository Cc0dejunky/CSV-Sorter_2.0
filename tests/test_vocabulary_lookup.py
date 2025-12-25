import io
import pytest
from fastapi.testclient import TestClient
from main import app
from db_adapter import get_connection, ensure_tables
from scripts.seed_vocabulary import seed as seed_vocab


def test_upload_csv_uses_vocabulary(tmp_path):
    ensure_tables()
    # Clear products
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM products"); cur.execute("DELETE FROM feedback"); conn.commit()
    cur.close(); conn.close()

    # Ensure vocabulary seeded
    seed_vocab()

    client = TestClient(app)

    csv_content = "text\nNvy Blue T-shirt\nRd Shirt\n"
    files = {
        'file': ('test.csv', csv_content, 'text/csv')
    }
    res = client.post('/upload-csv', files=files)
    assert res.status_code == 200

    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT text_content, normalized_value, confidence, needs_review FROM products ORDER BY id DESC LIMIT 2")
    rows = cur.fetchall()
    cur.close(); conn.close()

    # One or both should be mapped by vocabulary (nvy->Navy or rd->Red)
    assert any((r[1] and r[2] == 1.0 and r[3] == 0) for r in rows)
