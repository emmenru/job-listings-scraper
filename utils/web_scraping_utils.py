# Standard library imports
import re
import time
import math
import random

# Third-party library imports
import requests
from bs4 import BeautifulSoup
from lxml import etree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Function to get DOM from the given URL
def get_dom(url):
    """Retrieves the Document Object Model (DOM) from the provided URL.

    Handles WebDriver exceptions by restarting the browser if necessary.

    Args:
        url (str): The URL to retrieve the DOM from.

    Returns:
        lxml.etree.ElementTree: The DOM representation of the webpage.
        None: If an error occurs while retrieving the DOM.
    """
    global driver
    try:
        driver.get(url)
        # Ensure page loads (consider using WebDriverWait instead)
        time.sleep(random.uniform(2, 5))
        page_content = driver.page_source
        product_soup = BeautifulSoup(page_content, 'html.parser')
        dom = et.HTML(str(product_soup))
        return dom
    except WebDriverException as e:
        print("WebDriver disconnected, restarting the browser:", e)
        driver.quit()
        driver = initialize_driver()
        return None

# Functions to extract job details

def get_job_link(job):
    """Extracts the job link from the provided job element using XPath.

    Handles potential errors by returning 'Not available' if the link cannot be found.

    Args:
        job (lxml.etree.Element): The job element to extract the link from.

    Returns:
        str: The URL of the job listing.
        str: 'Not available' if the link cannot be found.
    """
    try:
        return job.xpath('./descendant::h2/a/@href')[0]
    except Exception:
        return 'Not available'

def get_job_desc(job_link):
    """Extracts the job description from the provided job link.

    Fetches the DOM using get_dom() and then extracts the description text.

    Args:
        job_link (str): The URL of the job listing.

    Returns:
        str: The job description text.
        str: 'Not available' if the description cannot be found.
    """
    job_dom = get_dom(job_link)
    try:
        job_desc = job_dom.xpath('//*[@id="jobDescriptionText"]//text()')
        return " ".join(job_desc).strip() if job_desc else 'Not available'
    except Exception:
        return 'Not available'

def get_company_name(job):
    """Extracts the company name from the provided job element using XPath.

    Handles potential errors by returning 'Not available' if the company name cannot be found.

    Args:
        job (lxml.etree.Element): The job element to extract the company name from.

    Returns:
        str: The company name.
        str: 'Not available' if the company name cannot be found.
    """
    try:
        company_name = job.xpath('.//span[@data-testid="company-name"]/text()')[0]
    except Exception:
        company_name = 'Not available'
    return company_name

def get_company_location(job):
    """Extracts the company location from the provided job element using XPath.

    Handles potential errors by returning 'Not available' if the company location cannot be found.

    Args:
        job (lxml.etree.Element): The job element to extract the company location from.

    Returns:
        str: The company location.
        str: 'Not available' if the company location cannot be found.
    """
    try:
        company_location = job.xpath('.//div[@data-testid="text-location"]/text()')[0]
    except Exception:
        company_location = 'Not available'
    return company_location

def get_salary(job_link):
    """Extracts the salary information from the provided job link.

    Fetches the DOM using get_dom() and then extracts the salary text.

    Args:
        job_link (str): The URL of the job listing.

    Returns:
        str: The salary information.
        str: 'Not available' if the salary cannot be found.
    """
    job_dom = get_dom(job_link)
    try:
        salary = job_dom.xpath('//*[@id="salaryInfoAndJobType"]//text()')
        return " ".join(salary).strip() if salary else 'Not available'
    except Exception:
        return 'Not available'

def get_total_pages(driver, job_keyword, location_keyword, base_url):
    """Calculates the total number of pages based on the estimated number of jobs.

    Uses WebDriverWait to ensure element presence before extracting job count text.
    Extracts digits using regular expressions and calculates total pages based on jobs per page.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        job_keyword (str): The keyword to search for jobs.
        location_keyword (str): The location keyword for job search.
        base_url (str): The base URL of the job search website.

    Returns:
        int: The estimated total number of pages containing jobs.
        0: If an error occurs or no jobs are found.
    """
    url = f"{base_url}/jobs?q={job_keyword}&l={location_keyword}"
    driver.get(url)
    try:
        job_count_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "jobsearch-JobCountAndSortPane-jobCount")]'))
        )
        job_count_text = job_count_element.text
        print(f"Job count text: {job_count_text}")

        # Use regex to find all digits in the job_count_text and join them together
        job_count = int(''.join(re.findall(r'\d+', job_count_text)))  # Extract only digits

        print(f"Parsed job count: {job_count}")

        # If job count is 0 or not available, handle that gracefully
        if job_count == 0:
            print("No jobs found.")
            return 0

        # Number of jobs listed per page (Indeed typically lists 15 per page)
        jobs_per_page = 15

        # Calculate total number of pages, rounding up
        total_pages = math.ceil(job_count / jobs_per_page)
        return total_pages

    except Exception as e:
        print(f"Error extracting job count: {e}")
        return 0