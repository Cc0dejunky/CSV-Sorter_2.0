import csv
import sqlite3
import os

def ingest_direct(file_path):
    db_path = "dev.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # This creates the table with the status column from the start
        cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, text_content TEXT, status TEXT)")
        
        count = 0
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found.")
            return

        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                handle = row.get('Handle', '').strip()
                title = row.get('Title', '').strip()
                if handle and title:
                    combined = f"{handle} | {title}"
                    cursor.execute("INSERT INTO products (text_content, status) VALUES (?, ?)", (combined, 'pending'))
                    count += 1
        
        conn.commit()
        conn.close()
        print(f"SUCCESS: {count} products added to the database!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ingest_direct("Shopify-Short.csv")