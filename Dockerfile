FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure data directory exists for SQLite
RUN mkdir -p /app/data

# Expose the API port
EXPOSE 8000

# Start the application using a production ASGI server with Gunicorn 
# UvicornWorkers allow FastAPI native async processing
CMD ["gunicorn", "src.api.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
