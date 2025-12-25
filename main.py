import os
import psycopg2
import csv
import io
import boto3
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from pgvector.psycopg2 import register_vector
from AI_Project_Root.retrain_model import retrain

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
# Defaults to 'db' (Docker service name), but can be overridden for local testing
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
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

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
    conn = get_db_connection()
    register_vector(conn)
    cur = conn.cursor()
    # Fetch products that don't have feedback yet
    cur.execute("""
        SELECT p.id, p.text_content 
        FROM products p
        LEFT JOIN feedback f ON p.id = f.product_id
        WHERE f.id IS NULL
        LIMIT 10
    """)
    products = cur.fetchall()
    
    results = []
    for p_id, p_text in products:
        # Get the vector for the current product
        cur.execute("SELECT vector FROM embeddings WHERE product_id = %s", (p_id,))
        embedding_row = cur.fetchone()
        
        confidence = 0.0
        suggestion = None
        
        if embedding_row:
            current_vector = embedding_row[0]
            # Find the nearest approved product to calculate confidence
            cur.execute("""
                SELECT p.text_content, e.vector <=> %s AS distance
                FROM embeddings e
                JOIN feedback f ON e.product_id = f.product_id
                JOIN products p ON e.product_id = p.id
                WHERE f.is_approved = TRUE
                ORDER BY distance ASC
                LIMIT 1
            """, (current_vector,))
            neighbor = cur.fetchone()
            
            if neighbor:
                neighbor_text, distance = neighbor
                # Convert cosine distance to a confidence score (0 to 1)
                confidence = max(0, 1 - distance)
                suggestion = neighbor_text
        
        results.append({
            "id": p_id, 
            "text": p_text,
            "confidence": round(confidence, 2),
            "suggestion": suggestion
        })

    cur.close()
    conn.close()
    
    return results

@app.post("/submit-feedback")
def submit_feedback(feedback: Feedback):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feedback (product_id, is_approved, correction)
        VALUES (%s, %s, %s)
    """, (feedback.product_id, feedback.is_approved, feedback.correction))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    # Read the file content
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
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Skip the header row
    next(csv_reader, None)
    
    count = 0
    for row in csv_reader:
        if row:
            # Assuming the first column contains the product text
            cur.execute("INSERT INTO products (text_content) VALUES (%s)", (row[0],))
            count += 1
            
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Successfully uploaded {count} products"}

@app.post("/trigger-retrain")
async def trigger_retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(retrain)
    return {"message": "Retraining started in background"}