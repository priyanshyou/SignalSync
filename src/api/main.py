from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from src.pipeline.database import get_recent_jobs, init_db
from src.automation.scheduler import start_scheduler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import io
import os

app = FastAPI(title="Coherent B2B Data Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoint for data access
@app.get("/api/leads")
def get_leads(limit: int = 100):
    """Returns the most recent hiring signals from the database"""
    jobs = get_recent_jobs(limit=limit)
    return {"data": jobs, "count": len(jobs)}

@app.get("/api/search")
def semantic_search(q: str, limit: int = 20):
    """Semantic vector search using TF-IDF for RAG-like matching"""
    jobs = get_recent_jobs(limit=500)
    if not jobs or not q.strip():
        return {"data": jobs[:limit]}

    df = pd.DataFrame(jobs)
    # Create the document representation for each job
    corpus = (df['title'].fillna('') + ' ' + 
              df['tech_stack'].fillna('') + ' ' + 
              df['category'].fillna('') + ' ' + 
              df['job_types'].fillna('')).tolist()
    
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vec = vectorizer.transform([q])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
        df['similarity'] = similarities
        
        # Sort and filter
        df_sorted = df.sort_values(by='similarity', ascending=False)
        df_filtered = df_sorted[df_sorted['similarity'] > 0.01].copy()
        
        # Drop the similarity score before sending to frontend
        df_filtered.drop(columns=['similarity'], inplace=True, errors='ignore')
        
        result = df_filtered.head(limit).to_dict(orient='records')
        return {"data": result}
    except Exception as e:
        print(f"Search error: {e}")
        return {"data": jobs[:limit]} # fallback

@app.get("/api/export")
def export_csv():
    """Export the clean data as a CRM-ready CSV"""
    jobs = get_recent_jobs(limit=1000)
    if not jobs:
         return PlainTextResponse("No Data", media_type="text/csv")
    df = pd.DataFrame(jobs)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return PlainTextResponse(output.read(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=leads_report.csv"})

# Mount the static frontend directory
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.on_event("startup")
def on_startup():
    init_db()
    # Start the background pipeline scraper
    start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
