from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# This allows your React app to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "dev.db"

class ProductUpdate(BaseModel):
    status: str = None
    text_content: str = None

@app.get("/products")
def get_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, text_content, status FROM products")
        rows = cursor.fetchall()
        return [{"id": r[0], "text_content": r[1], "status": r[2]} for r in rows]
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.post("/products/{product_id}")
def update_product(product_id: int, update: ProductUpdate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if update.status:
            cursor.execute("UPDATE products SET status = ? WHERE id = ?", (update.status, product_id))
        if update.text_content:
            cursor.execute("UPDATE products SET text_content = ? WHERE id = ?", (update.text_content, product_id))
        conn.commit()
        return {"message": "Updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
