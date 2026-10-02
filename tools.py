import pandas as pd
import numpy as np

def retail_analyzer(file_path: str):
    # 1. Load data
    df = pd.read_csv(file_path)
    
    # Normalize headers
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # --- Q3: Data Quality Issues (STRICT COUNTS) ---
    # duplicate order IDs
    duplicates = df.duplicated(subset=['order_id']).sum()
    
    # quantity outliers (>1000)
    outliers = len(df[pd.to_numeric(df['quantity'], errors='coerce') > 1000])
    
    # price format errors 
    # (Matches ₹ symbols or other non-numeric characters found in your CSV)
    price_errors = df['unit_price'].astype(str).str.contains('[^0-9.]', regex=True).sum()
    
    # invalid discounts (not between 0-100)
    # coerce handles nulls/strings so we don't crash here
    disc_numeric = pd.to_numeric(df['discount_percent'], errors='coerce')
    invalid_discounts = len(df[(disc_numeric < 0) | (disc_numeric > 100)])
    
    # total null cells
    total_nulls = df.isnull().sum().sum()
    
    q3_result = (f"Duplicate Order IDs: {duplicates}, Quantity Outliers (>1000): {outliers}, "
                 f"Price Format Errors: {price_errors}, Invalid Discounts: {invalid_discounts}, "
                 f"Total Null Cells: {total_nulls}")

    # --- Data Cleaning for Math ---
    # We strip currency symbols so math doesn't fail
    df['unit_price'] = df['unit_price'].astype(str).str.replace('₹', '').str.replace(',', '')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0)
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df['discount_percent'] = pd.to_numeric(df['discount_percent'], errors='coerce').fillna(0)
    
    # --- Q1: Total Revenue per Category ---
    df['revenue'] = df['quantity'] * df['unit_price'] * (1 - df['discount_percent']/100)
    q1 = df.groupby('product_category')['revenue'].sum().sort_values(ascending=False).to_dict()

    # --- Q2: Average Delivery Time (FIXED COLUMN NAME) ---
    # Your CSV had 'delivery_days', not 'delivery_date'
    q2 = df.groupby('customer_region')['delivery_days'].mean().sort_values(ascending=False).to_dict()

    # --- Q4: Return Rate (%) ---
    # return_status is the column name from your sample
    returns = df[df['return_status'].str.lower() == 'returned'].groupby('payment_method').size()
    totals = df.groupby('payment_method').size()
    q4 = ((returns / totals) * 100).fillna(0).sort_values(ascending=False).to_dict()

    return {
        "Q1": q1, "Q2": q2, "Q3": q3_result, "Q4": q4, 
        "summary_context": df.describe().to_string()
    }