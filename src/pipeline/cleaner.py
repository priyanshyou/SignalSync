import pandas as pd
import logging
from src.pipeline.ai_enrichment import enrich_tech_stack
from datetime import datetime

# Helper function to parse dates robustly
def parse_date(date_str):
    if pd.isna(date_str) or date_str == "":
        return datetime.now().strftime('%Y-%m-%d')
        
    date_str = str(date_str).replace('Posted:', '').strip()
    try:
        # Tries to parse '15 April 2026' format
        parsed = datetime.strptime(date_str, '%d %B %Y')
        return parsed.strftime('%Y-%m-%d')
    except ValueError:
        pass
        
    try:
         return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except Exception:
         return datetime.now().strftime('%Y-%m-%d')

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
        
    logging.info(f"Cleaning {len(df)} rows...")
    
    # 1. Drop complete duplicates
    df = df.drop_duplicates(subset=['url'])
    
    # 2. Handle missing essential fields
    df = df.dropna(subset=['title', 'url'])
    
    # 3. Standardize dates
    df['date_posted'] = df['date_posted'].apply(parse_date)
    
    # 4. Clean locations and companies
    df['location'] = df['location'].fillna("Unknown").str.strip()
    df['company'] = df['company'].fillna("Unknown").str.strip()
    
    # 5. Enrich with AI
    df = enrich_tech_stack(df)
    
    # Replace remaining NaNs with empty strings for safe DB insertion
    df = df.fillna("")
    
    logging.info(f"Finished cleaning. {len(df)} rows remaining.")
    return df
