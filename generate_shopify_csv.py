import sqlite3
import csv
import re

def slugify(text):
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')

def run_export():
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()
    
    # Using the columns we KNOW exist: text_content and status
    try:
        cursor.execute("SELECT id, text_content, normalized_value FROM products WHERE status IN ('approved', 'corrected')")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")
        return

    if not rows:
        print("⚠️ No reviewed products found! Did you finish your reviews in the dashboard?")
        return

    with open('shopify_import.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Shopify Headers
        writer.writerow(['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Variant Price'])

        for row in rows:
            p_id, clean_title, norm_val = row
            
            # Handle for the URL
            handle = slugify(clean_title)
            
            # Tags: Using the Intent Formula (Device + Type)
            tags = f"Electronics, {clean_title}"
            
            # Price Logic: Since final_price isn't in the DB, we'll set a default 
            # or you can put a specific number here like "19.99"
            price = "29.99" 

            body = f"<p>High-quality {clean_title}. Optimized for your daily needs.</p>"

            writer.writerow([
                handle, 
                clean_title, 
                body, 
                "My Store", 
                "Electronics", 
                tags, 
                "TRUE", 
                price
            ])

    conn.close()
    print(f"🚀 Success! {len(rows)} products exported to 'shopify_import.csv'.")

if __name__ == "__main__":
    run_export()