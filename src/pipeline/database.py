import sqlite3
import pandas as pd
import logging
from pathlib import Path

DB_PATH = Path("data/jobs.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            url TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            date_posted TEXT,
            job_types TEXT,
            category TEXT,
            tech_stack TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
def upsert_jobs(df: pd.DataFrame):
    if df.empty:
        return
    conn = sqlite3.connect(DB_PATH)
    records = df.to_dict('records')
    cursor = conn.cursor()
    
    for row in records:
        cursor.execute('''
            INSERT INTO jobs (url, title, company, location, date_posted, job_types, category, tech_stack)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                date_posted = excluded.date_posted,
                job_types = excluded.job_types,
                category = excluded.category,
                tech_stack = excluded.tech_stack
        ''', (
              row.get('url', ''), 
              row.get('title', ''), 
              row.get('company', ''), 
              row.get('location', ''), 
              row.get('date_posted', ''), 
              row.get('job_types', ''), 
              row.get('category', ''), 
              row.get('tech_stack', '')
        ))
    
    conn.commit()
    conn.close()
    logging.info(f"Upserted {len(records)} jobs to database.")

def get_recent_jobs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY date_posted DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]
