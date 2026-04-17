import pandas as pd
import re

COMMON_TECHS = [
    "Python", "Django", "Flask", "FastAPI", "React", "Vue", "Angular",
    "SQL", "PostgreSQL", "MySQL", "NoSQL", "MongoDB", "Redis",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "CI/CD", "Machine Learning",
    "Data Science", "Pandas", "PyTorch", "TensorFlow", "Generative AI", "LLM"
]

def extract_techs(text: str):
    if not isinstance(text, str):
         return ""
    found = []
    text_lower = text.lower()
    for tech in COMMON_TECHS:
        # Simple word boundary regex, handle cases like C++ or CI/CD later if needed
        # Escape special characters for matching
        pattern = r'\b' + re.escape(tech.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(tech)
            
    # Guarantee Python is there since its python.org! (Unless explicitly not)
    if "Python" not in found:
        found.append("Python")
        
    return ", ".join(found)

def enrich_tech_stack(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simulates an AI layer extracting structured insights from raw text.
    In a real scenario, this would likely query an LLM or use an embedding similarity search
    to match unstructured description to known entities.
    """
    if df.empty:
        return df
        
    df['combined_text'] = df['title'] + " " + df['job_types'] + " " + df['category']
    df['tech_stack'] = df['combined_text'].apply(extract_techs)
    df = df.drop(columns=['combined_text'])
    return df
