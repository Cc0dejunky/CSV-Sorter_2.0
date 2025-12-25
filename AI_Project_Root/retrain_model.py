import os
import psycopg2
import boto3
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

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
            host=DB_HOST,
        )
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def upload_directory_to_r2(local_path, bucket_name, r2_prefix):
    """Uploads a directory (the model) to Cloudflare R2."""
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv("R2_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
    )
    
    for root, dirs, files in os.walk(local_path):
        for file in files:
            local_file = os.path.join(root, file)
            # Calculate relative path for S3 key
            relative_path = os.path.relpath(local_file, local_path)
            s3_key = os.path.join(r2_prefix, relative_path)
            
            print(f"Uploading {local_file} to R2...")
            s3.upload_file(local_file, bucket_name, s3_key)
    print("Model backup to R2 complete.")

def retrain():
    conn = get_db_connection()
    if not conn:
        return

    cur = conn.cursor()
    
    # Fetch pairs: (Original Text, Corrected Text)
    # We only want items where a human actually provided a correction
    cur.execute("""
        SELECT p.text_content, f.correction 
        FROM feedback f 
        JOIN products p ON f.product_id = p.id 
        WHERE f.correction IS NOT NULL AND f.correction != ''
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if len(rows) < 5:
        print(f"Not enough data to retrain. Found {len(rows)} corrections, need at least 5.")
        return

    print(f"Starting retraining with {len(rows)} correction pairs...")

    # 1. Prepare Data: Create pairs of (Input, Label)
    train_examples = [InputExample(texts=[row[0], row[1]]) for row in rows]
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

    # 2. Load Model: Start with the base model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 3. Define Loss: This loss pulls the vector of the 'correction' closer to the 'original'
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # 4. Train
    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=10)

    # 5. Save: Overwrite the local model or save to a new versioned path
    save_path = "./fine_tuned_model"
    model.save(save_path)
    print(f"Model fine-tuned and saved to {save_path}")

    # 6. Backup to R2
    if os.getenv("R2_BUCKET_NAME"):
        upload_directory_to_r2(save_path, os.getenv("R2_BUCKET_NAME"), "models/latest")

if __name__ == "__main__":
    retrain()
