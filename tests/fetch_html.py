import requests
from bs4 import BeautifulSoup

res = requests.get('https://www.python.org/jobs/')
soup = BeautifulSoup(res.text, 'html.parser')
job_list = soup.find('ol', class_='list-recent-jobs')
if job_list:
    item = job_list.find('li')
    if item:
        print(item.prettify())
else:
    print("No job list found.")
