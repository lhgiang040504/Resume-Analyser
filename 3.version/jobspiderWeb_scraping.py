
import requests
from bs4 import BeautifulSoup # commonly used for parsing HTML content
import time # introduce delays between steps in your code
import pandas as pd

# Get resume links from link of pages
def get_resume(url='https://www.jobspider.com/job/resume-search-results.asp/words_Software%2BEngineer'):
    href_list = []

    domains_list = url
    for domain in domains_list:
        for j in range(1, 30):
            print(f'The function takes 30 pages, which is the maximum at the present time of {url}')
            url = domain + f'/page_{j}'

            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links that we need on the page
            href_locals = soup.find_all('a', attrs={'href': True}, href=lambda value: value.startswith('/job/view-resume-'))
            try:
                for href_local in href_locals:
                    href_list.append('https://www.jobspider.com' + href_local['href'])
            except:
                pass

    return href_list

# Convert resume into text
def resume_to_text(url):
	# Create file to store data
    file_name = url[30:-5] + '.txt'
	
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'lxml')

    # Get job function sought
    resume_type = soup.find_all(["h1"])[0].text.strip()

    # Get job decription
    decriptions = soup.find_all(["td"])
    return file_name, resume_type, [decription.text.strip() for decription in decriptions]
