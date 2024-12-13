# job-listings-scraper

This repository contains code for scraping and analyzing job listings data from Indeed, focusing on Data Science roles across different countries. The project provides insights into salary ranges, technical requirements, and role definitions across major cities in the USA, France, Italy, and Sweden.

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Descriptions](#file-descriptions)
3. [Setup and Installation](#setup-and-installation)
4. [Important Notes](#important-notes)

## Project Overview

This project analyzes Data Science job market trends through automated scraping of Indeed job listings. The analysis reveals salary disparities, varying technical requirements, and different role definitions across countries and position titles.

### Background
Data Science remains a dynamic field with evolving role definitions. The terminology used to describe positions like Data Scientist, Data Analyst, and BI Analyst varies significantly across companies and countries, creating ambiguity in job market analysis. This project provides a snapshot of the Data Science job market in September 2024, based on Indeed job listings.

### Aim
To analyze and compare Data Science job roles across major cities in France, Italy, Sweden, and the USA through automated scraping of Indeed job listings, focusing on role requirements, technical skills, and salary distributions.

### Approach
- Data Collection: Scraped Indeed job listings for 'Data Scientist', 'Data Analyst', 'Product Analyst', and 'BI Scientist'
- Coverage: Three largest cities per country
- Timeframe: Data collected September 19th (USA, Sweden) and 20th (France, Italy) 2024
- Analysis: Statistical comparison of roles and salaries across regions using Python and Tableau

### Findings
Please refer to step **4. View Results** below. A brief summary is presented at the end of the EDA.ipynb notebook.  

## File Descriptions

### Notebooks
- **scraper-countries.ipynb**: Jupyter Notebook for scraping job listing data using BeautifulSoup and Selenium
- **EDA.ipynb**: Jupyter Notebook for data cleaning, formatting, exploratory data analysis, feature extraction and statistical analysis
- **Dashboard.twb**: Tableau dashboard summarizing the analysis results

### Data
- **data/**: Directory containing scraped job listings data
  - **processed/**: Cleaned and processed data used for Tableau visualization

### Utils
- **utils/web_scraping_utils.py**: Helper functions for web scraping
- **utils/preprocessor.py**: Initial data processing and preparation functions
- **utils/salary_extractor.py**: Functions for extracting numerical salary values from text
- **utils/text_parser.py**: Text processing functions using NLTK
- **utils/analysis.py**: Statistical analysis functions
- **utils/dictionaries.py**: Mapping dictionaries for technical skills and language configurations
- **utils/plotting.py**: Visualization functions

### Configuration
- **requirements.txt**: Python package dependencies

## Setup and Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/emmenru/job-listings-scraper.git
    cd job-listings-scraper
    ```

2. **Environment Setup**:
    - Install Firefox if you don't already have it (required for web scraping). 
    - Install Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    I use a virtual environment to isolate project dependencies, launched in Jupyter Notebook using ipykernel (see e.g. https://janakiev.com/blog/jupyter-virtual-envs/).

3. **Run the Analysis**:
    - Execute notebooks in order:
        1. `scraper-countries.ipynb` for data collection
        2. `EDA.ipynb` for analysis

4. **View Results**:
    - The final dashboard can be viewed on [Tableau Public](https://public.tableau.com/app/profile/emma.frid/viz/DataScienceJobMarketAnalysis_17340041213390/Dashboard2)
    - Additional project details are available on the [portfolio page](https://sites.google.com/view/emmafrid/project-page-7?authuser=0)

## Important Notes

### Web Scraping Considerations
- Ensure all scraping activities comply with website policies and terms of service
- Check the Indeed robots.txt file (https://www.indeed.com/robots.txt) for allowed/disallowed activities
- Non-compliance with these policies may result in legal issues or IP bans

### Technical Considerations
- Prevent machine sleep mode during scraping to maintain stable connections
- Consider reducing request volume (fewer job titles or cities) if connection issues arise
- Be aware that filtering properties may vary between countries on Indeed
- All search keywords were in English
