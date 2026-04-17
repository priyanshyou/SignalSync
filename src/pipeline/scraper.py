import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class JobScraper:
    def __init__(self, base_url="https://www.python.org/jobs/?page={}"):
        self.base_url = base_url
    
    def fetch_page(self, page_num):
        url = self.base_url.format(page_num)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        jobs_data = []
        
        job_list = soup.find('ol', class_='list-recent-jobs')
        if not job_list:
            return jobs_data
            
        for job in job_list.find_all('li'):
            try:
                title_elem = job.find('h2').find('a') if job.find('h2') else None
                title = title_elem.text.strip() if title_elem else "Unknown Title"
                job_url = "https://www.python.org" + title_elem['href'] if title_elem else ""

                # Company name is a text entity within listing-company-name
                company_span = job.find('span', class_='listing-company-name')
                # Usually text after the <a> tag
                company = company_span.text.split('\n')[-2].strip() if company_span else "Unknown Company"
                if not company or company == "New":
                     # Fallback to general text parsing if needed
                     pass

                location_elem = job.find('span', class_='listing-location')
                location = location_elem.text.strip() if location_elem else "Unknown Location"
                
                date_elem = job.find('time')
                date_posted = date_elem.text.strip() if date_elem else ""
                
                type_elems = job.find_all('span', class_='listing-job-type')
                job_types = [t.text.strip() for t in type_elems] if type_elems else []

                category_elem = job.find('span', class_='listing-company-category')
                category = category_elem.text.strip() if category_elem else ""
                
                jobs_data.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "date_posted": date_posted,
                    "job_types": ", ".join(job_types),
                    "category": category,
                    "url": job_url
                })
            except Exception as e:
                logging.error(f"Error parsing a job entry: {e}")
                
        return jobs_data

    def run(self, pages=5):
        all_jobs = []
        for page in range(1, pages + 1):
            logging.info(f"Scraping page {page}...")
            html = self.fetch_page(page)
            if not html:
                continue
            
            jobs = self.parse_jobs(html)
            if not jobs:
                logging.info("No more jobs found.")
                break
                
            all_jobs.extend(jobs)
            time.sleep(1) # Be polite to the server
            
        df = pd.DataFrame(all_jobs)
        logging.info(f"Scraped a total of {len(df)} jobs.")
        return df

if __name__ == "__main__":
    scraper = JobScraper()
    df = scraper.run(pages=3)
    df.to_csv("data/raw_jobs.csv", index=False)
    print(df.head())
