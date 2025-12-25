"""Create clusters from stored product embeddings and save a cluster report.

- Reads `embeddings.vector_json` and product metadata from the DB.
- Runs KMeans clustering (n_clusters default 18, configurable via --n).
- Finds the 5 most central products per cluster and writes `cluster_report.txt`.

Usage:
    python scripts/generate_clusters.py --n 18 --out cluster_report.txt
"""
import argparse
import json
import math
from statistics import mean
from db_adapter import get_connection, ensure_tables
import numpy as np
from sklearn.cluster import KMeans


def load_embeddings():
    ensure_tables()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT e.product_id, e.vector_json, p.text_content, p.normalized_value, p.confidence FROM embeddings e JOIN products p ON p.id = e.product_id WHERE e.vector_json IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    items = []
    for r in rows:
        pid = r[0]
        vec_s = r[1]
        try:
            vec = json.loads(vec_s)
        except Exception:
            try:
                vec = eval(vec_s)
            except Exception:
                print(f"Skipping embedding for product {pid}: cannot parse vector")
                continue
        items.append((pid, np.array(vec, dtype=float), r[2], r[3], float(r[4] or 0.0)))
    return items


def cluster_and_report(n_clusters=18, out_path='cluster_report.txt'):
    items = load_embeddings()
    if not items:
        print("No embeddings found in DB. Run embedding worker first or insert embeddings.")
        return False

    X = np.vstack([it[1] for it in items])
    n_clusters = min(n_clusters, len(items))
    print(f"Clustering {len(items)} embeddings into {n_clusters} clusters...")
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    centers = km.cluster_centers_

    clusters = {i: [] for i in range(n_clusters)}
    for idx, lab in enumerate(labels):
        pid, vec, text, norm, conf = items[idx]
        clusters[lab].append((pid, vec, text, norm, conf))

    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(f"Cluster report: {len(items)} embeddings, k={n_clusters}\n\n")
        for k in sorted(clusters.keys()):
            members = clusters[k]
            fh.write(f"Cluster {k}: {len(members)} items\n")
            # compute distance to center
            dists = []
            for pid, vec, text, norm, conf in members:
                center = centers[k]
                dist = np.linalg.norm(vec - center)
                dists.append((dist, pid, text, norm, conf))
            dists.sort(key=lambda x: x[0])
            fh.write("  Central items:\n")
            for dist, pid, text, norm, conf in dists[:5]:
                fh.write(f"    - id={pid} dist={dist:.4f} conf={conf:.2f} text={text!r} normalized={norm!r}\n")
            fh.write('\n')
    print(f"Wrote cluster report to {out_path}")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=18, help='Number of clusters (15-20 recommended)')
    parser.add_argument('--out', default='cluster_report.txt')
    args = parser.parse_args()
    cluster_and_report(n_clusters=args.n, out_path=args.out)
