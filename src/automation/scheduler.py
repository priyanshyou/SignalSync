import logging
from apscheduler.schedulers.background import BackgroundScheduler
from src.pipeline.scraper import JobScraper
from src.pipeline.cleaner import clean_data
from src.pipeline.database import init_db, upsert_jobs
from datetime import datetime

logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("Starting data pipeline execution...")
    try:
        scraper = JobScraper()
        df = scraper.run(pages=3)
        if df.empty:
            logger.info("No jobs scraped.")
            return

        df_cleaned = clean_data(df)
        upsert_jobs(df_cleaned)
        logger.info("Pipeline execution completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

def start_scheduler():
    init_db()
    # Run the pipeline immediately on start
    run_pipeline()
    
    scheduler = BackgroundScheduler()
    # Schedule to run every hour
    scheduler.add_job(run_pipeline, 'interval', hours=1)
    scheduler.start()
    logger.info("Job scheduler started.")
    return scheduler

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_scheduler()
    input("Press Enter to exit...\n")
