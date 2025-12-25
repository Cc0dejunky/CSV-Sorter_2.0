from db_adapter import get_connection, ensure_tables
from fastapi.testclient import TestClient
from main import app


def test_taxonomy_semantic_lookup(tmp_path):
    ensure_tables()
    conn = get_connection(); cur = conn.cursor()
    # Insert a deterministic taxonomy row for the test
    cur.execute("INSERT INTO taxonomy_reference (taxonomy_id, taxonomy_path, label) VALUES (?, ?, ?)", ('999999', 'Apparel > Shirts > Polo Shirts', 'Polo Shirts'))
    conn.commit()
    # Clear products
    cur.execute("DELETE FROM products"); cur.execute("DELETE FROM feedback"); conn.commit()
    cur.close(); conn.close()

    client = TestClient(app)
    csv_content = "text\nPolo tee\n"
    files = {
        'file': ('test.csv', csv_content, 'text/csv')
    }
    res = client.post('/upload-csv', files=files)
    assert res.status_code == 200

    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT text_content, normalized_value, confidence, needs_review FROM products ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close(); conn.close()

    assert row is not None
    # Expect taxonomy match to produce 'Polo Shirts' or similar and confidence >= 0.85
    assert row[1] is not None
    assert row[2] >= 0.85
