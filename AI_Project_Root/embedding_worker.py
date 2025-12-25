import os
import time
import psycopg2
from sentence_transformers import SentenceTransformer

# Database Configuration
DB_NAME = os.getenv("POSTGRES_DB", "app_db")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "db")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def run_worker():
    """Main loop that processes new products and generates embeddings."""
    print("Initializing AI Model (SentenceTransformer)...")
    # This model converts text into a 384-dimensional vector
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully.")

    while True:
        conn = get_db_connection()
        if not conn:
            time.sleep(5)
            continue

        try:
            cur = conn.cursor()
            
            # 1. READ: Find products that don't have an embedding yet
            # This query looks for products where the join to 'embeddings' is NULL
            cur.execute("""
                SELECT p.id, p.text_content 
                FROM products p
                LEFT JOIN embeddings e ON p.id = e.product_id
                WHERE e.product_id IS NULL
                LIMIT 50
            """)
            rows = cur.fetchall()

            if not rows:
                # No new data, wait before checking again
                print("No new products found. Sleeping...")
                time.sleep(5)
            else:
                print(f"Processing {len(rows)} new products...")
                
                for product_id, text_content in rows:
                    # 2. PROCESS: The AI 'reads' the text and creates a vector
                    if text_content:
                        embedding_vector = model.encode(text_content).tolist()
                        
                        # 3. WRITE: Save the vector so we can 'check' it later
                        cur.execute("""
                            INSERT INTO embeddings (product_id, vector)
                            VALUES (%s, %s)
                        """, (product_id, embedding_vector))
                    else:
                        print(f"Skipping product {product_id} (empty text)")

                conn.commit()
                print("Batch processed and saved.")

            cur.close()
            conn.close()

        except Exception as e:
            print(f"Error during processing: {e}")
            if conn:
                conn.close()
            time.sleep(5)

if __name__ == "__main__":
    # Add a small delay to ensure DB is ready on startup
    time.sleep(10)
    run_worker()