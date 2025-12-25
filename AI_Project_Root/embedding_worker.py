import time
import sqlite3
import json
from sentence_transformers import SentenceTransformer
from db_adapter import get_connection

def run_worker():
    print("Initializing AI Model (SQLite Version)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully.")

    while True:
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # 1. Find products without embeddings
            cur.execute("""
                SELECT p.id, p.text_content 
                FROM products p
                LEFT JOIN embeddings e ON p.id = e.product_id
                WHERE e.product_id IS NULL
                LIMIT 50
            """)
            rows = cur.fetchall()

            if not rows:
                print("No new products to process. Sleeping...")
                time.sleep(10)
            else:
                print(f"AI is processing {len(rows)} products...")
                for product_id, text_content in rows:
                    if text_content:
                        # Create the AI vector
                        vector = model.encode(text_content).tolist()
                        # Save to SQLite (using JSON string for the vector)
                        cur.execute("INSERT INTO embeddings (product_id, vector_json) VALUES (?, ?)", 
                                   (product_id, json.dumps(vector)))
                
                conn.commit()
                print("Batch completed.")

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_worker()