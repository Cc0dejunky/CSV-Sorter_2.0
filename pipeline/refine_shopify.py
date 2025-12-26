import pandas as pd
import argparse
import os

def refine(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    try:
        df = pd.read_csv(file_path)
        
        # 1. Filter: Only keep rows with images (as per your AppScript)
        if 'Variant Image' in df.columns:
            df = df.dropna(subset=['Variant Image'])
        
        # 2. Math: Calculate Pricing
        if 'Cost per item' in df.columns:
            # Convert to numeric, handle errors
            df['Cost per item'] = pd.to_numeric(df['Cost per item'], errors='coerce').fillna(0)
            df['Variant Price'] = df['Cost per item'] * 2
            df['Variant Compare At Price'] = df['Cost per item'] * 4
        
        # 3. Logic: Status and Taxable
        df['Status'] = 'active'
        df['Variant Taxable'] = 'TRUE'
        df['Variant Requires Shipping'] = 'TRUE'

        # 4. Clean Titles: If Title is missing, use Handle logic
        if 'Title' in df.columns and 'Handle' in df.columns:
            df['Title'] = df['Title'].fillna(df['Handle'].str.replace('-', ' ').str.title())

        # 5. Keep the columns you need for Shopify
        cols_to_keep = [
            'Handle', 'Title', 'Product Category', 'Type', 'Tags', 
            'Status', 'Variant Price', 'Variant Compare At Price', 
            'Variant Taxable', 'Cost per item'
        ]
        
        # Only keep columns that actually exist in the file
        existing_cols = [c for c in cols_to_keep if c in df.columns]
        slim_df = df[existing_cols]

        output_file = "Shopify-Short.csv"
        slim_df.to_csv(output_file, index=False)
        
        print(f"--- Success! ---")
        print(f"Calculated pricing and set status to active.")
        print(f"Saved {len(slim_df)} products to {output_file}")
            
    except Exception as e:
        print(f"Failed to refine: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    refine(args.file)
