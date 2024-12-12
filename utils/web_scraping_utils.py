"""
Utility functions for web scraping job listings from Indeed.
Contains functions for browser initialization, DOM manipulation,
and data extraction from job listings.
"""

# Standard library imports
import math
import random
import re
import time
from csv import writer
from typing import Optional, Union, List

# Third-party library imports
from bs4 import BeautifulSoup
from lxml import etree as et
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

# Global variables
_driver: Optional[webdriver.Firefox] = None


# Basic helper functions 
def get_job_link(job: et._Element) -> str:
    '''Extract job link from job element.'''
    try:
        return job.xpath('./descendant::h2/a/@href')[0]
    except Exception:
        return 'Not available'


def get_job_title(job: et._Element) -> str:
    '''Extract job title from job element.'''
    try:
        job_title = job.xpath('./descendant::h2/a/span/text()')[0]
    except Exception:
        job_title = 'Not available'
    return job_title


def get_company_name(job: et._Element) -> str:
    '''Extract company name from job element.'''
    try:
        company_name = job.xpath('.//span[@data-testid="company-name"]/text()')[0]
    except Exception:
        company_name = 'Not available'
    return company_name


def get_company_location(job: et._Element) -> str:
    '''Extract company location from job element.'''
    try:
        company_location = job.xpath('.//div[@data-testid="text-location"]/text()')[0]
    except Exception:
        company_location = 'Not available'
    return company_location


# Core browser and DOM manipulation functions
def initialize_driver() -> webdriver.Firefox:
    '''Initialize and return a Firefox WebDriver instance.'''
    global _driver
    options = Options()
    service = Service(GeckoDriverManager().install())
    _driver = webdriver.Firefox(service=service, options=options)
    return _driver


def get_dom(url: str, driver: Optional[webdriver.Firefox] = None) -> Optional[et._Element]:
    '''Get DOM from the given URL.'''
    global _driver
    if driver:
        _driver = driver
    try:
        if not _driver:
            _driver = initialize_driver()
        _driver.get(url)
        wait = WebDriverWait(_driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(random.uniform(2, 5))
        page_content = _driver.page_source
        product_soup = BeautifulSoup(page_content, 'html.parser')
        dom = et.HTML(str(product_soup))
        return dom
    except WebDriverException as e:
        print('WebDriver disconnected, restarting the browser:', e)
        if _driver:
            _driver.quit()
        _driver = initialize_driver()
        return None


# Main data extraction functions
def get_total_pages(driver: webdriver.Firefox, 
                   job_keyword: str, 
                   location_keyword: str, 
                   base_url: str) -> int:
    '''Calculate total number of pages for job search results.'''
    url = f'{base_url}/jobs?q={job_keyword}&l={location_keyword}'
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 15)
        job_count_element = wait.until(
            EC.presence_of_element_located((By.XPATH, 
                '//div[contains(@class, "jobsearch-JobCountAndSortPane-jobCount")]'))
        )
        job_count_text = job_count_element.text
        print(f'Job count text: {job_count_text}')
        
        job_count = int(''.join(re.findall(r'\d+', job_count_text)))
        print(f'Parsed job count: {job_count}')
        
        if job_count == 0:
            print('No jobs found.')
            return 0
        
        jobs_per_page = 15
        total_pages = math.ceil(job_count / jobs_per_page)
        return total_pages
    except Exception as e:
        print(f'Error extracting job count: {e}')
        return 0

def get_job_desc(job_link: str) -> str:
    '''Extract job description from job link.'''
    job_dom = get_dom(job_link)
    try:
        job_desc = job_dom.xpath('//*[@id="jobDescriptionText"]//text()')
        return ' '.join(job_desc).strip() if job_desc else 'Not available'
    except Exception:
        return 'Not available'


def get_salary(job_link: str) -> str:
    '''Extract salary information from job link.'''
    job_dom = get_dom(job_link)
    try:
        salary = job_dom.xpath('//*[@id="salaryInfoAndJobType"]//text()')
        return ' '.join(salary).strip() if salary else 'Not available'
    except Exception:
        return 'Not available'

# Main scraping/orchestration functions
def process_job(job: et._Element, page_no: int, job_keyword: str, 
                location_keyword: str, selected_country: str, base_url: str) -> list:
    '''
    Process a single job listing and return its data as a list.
    '''
    job_link = base_url + get_job_link(job)
    return [
        page_no + 1,
        selected_country,
        job_link,
        job_keyword,
        location_keyword,
        get_job_title(job),
        get_company_name(job),
        get_company_location(job),
        get_salary(job_link),
        get_job_desc(job_link)
    ]


def scrape_jobs(csv_writer, driver: webdriver.Firefox, job_keywords: List[str], 
                location_keywords: List[str], selected_country: str, base_url: str) -> None:
    '''
    Main scraping function to process all jobs across pages and locations.
    '''
    for job_keyword in job_keywords:
        for location_keyword in location_keywords:
            print(f"Searching for: {job_keyword} in {location_keyword} ({selected_country})")
            total_pages = get_total_pages(driver, job_keyword, location_keyword, base_url)
            print(f"Total pages found in {location_keyword} in {selected_country}: {total_pages}")
            
            for page_no in range(total_pages):
                print(f"Fetching page {page_no + 1} for {job_keyword} in {location_keyword}")
                url = f"{base_url}/jobs?q={job_keyword}&l={location_keyword}&start={page_no * 10}"
                page_dom = get_dom(url, driver)
                
                if page_dom is None:
                    print(f"Failed to load page {page_no + 1}, skipping...")
                    continue
                
                jobs = page_dom.xpath('//div[@class="job_seen_beacon"]')
                print(f"Jobs found on page {page_no + 1}: {len(jobs)}")
                
                for job in jobs:
                    try:
                        record = process_job(job, page_no, job_keyword, 
                                          location_keyword, selected_country, base_url)
                        csv_writer.writerow(record)
                        time.sleep(random.uniform(2, 5))
                    except Exception as e:
                        print(f"Error processing job: {e}")