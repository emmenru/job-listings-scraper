import re
import requests

import numpy as np
import pandas as pd

#import matplotlib.pyplot as plt
#import seaborn as sns

import nltk
from nltk.corpus import stopwords
from collections import Counter

# Ensure NLTK stopwords are downloaded (run this once)
nltk.download('stopwords')

####### HELPER FUNCTIONS ####### 
    
def preprocess_text(text):
    # Remove punctuation and make lowercase
    return re.sub(r'[^\w\s]', '', text.lower())

def tokenize_and_filter(text, stop_words):
    # Tokenization: split text into words and remove stopwords
    tokens = text.split()
    return [word for word in tokens if word not in stop_words]
    
####### CLEANING, FORMATTING AND DESCRIBING DATA FRAME ####### 

def merge_US_cities(cities, DATA_PATH):
    """
    Args:
        cities: A list of US city names, abbreviated.
        DATA_PATH: The base path to the CSV files containing job listings.

    Returns:
        A DataFrame containing the merged job listings from the specified cities.

    Raises:
        ValueError: If the provided `cities` list is empty.
        FileNotFoundError: If any of the specified CSV files are not found.

    Note:
        The function assumes that the CSV files have a consistent structure, including column names and data types.

    """
    
    # Load data for the first city and add the 'country' column manually
    df_NY = pd.read_csv(f"{DATA_PATH}{'USA_'}{cities[0]}.csv")
    df_NY['country'] = 'USA'  # Add the 'country' column to match format
    print("Loaded data for", cities[0])

    # Load data for other cities
    df_LA = pd.read_csv(f"{DATA_PATH}{'USA_'}{cities[1]}.csv")
    df_CHI = pd.read_csv(f"{DATA_PATH}{'USA_'}{cities[2]}.csv")

    # Ensure consistent column order across DataFrames
    desired_order = df_LA.columns.tolist()
    df_NY = df_NY[desired_order]
    print("Column order for consistency:", desired_order)

    # Concatenate the DataFrames
    df_USA = pd.concat([df_NY, df_LA, df_CHI], ignore_index=True)

    # Verify column order consistency 
    assert df_USA.columns.tolist() == desired_order, "Column order mismatch!"

    return df_USA

def check_duplicates(data):
    """
    # Note: The number of rows should be equal to the number of unique job links, etc 
    """
    # Get the number of rows 
    num_rows = data.shape[0]
    # Print the number of rows
    print(f'The DataFrame has {num_rows} rows.')
    print(data.nunique()) 
    # Check for duplicates in all columns
    duplicates = data.duplicated(keep=False)
    # Print duplicate rows 
    print(data[duplicates])

def remove_duplicates_jobdesc(data):
    """
    Checks for duplicatse (same job description, location, and job title) in the DataFrame and keeps only the latest entry if a duplicate is identified. 

    Args:
        data: The input DataFrame containing job listings.

    Returns:
        A DataFrame with duplicate job listings removed. The latest occurrence of a duplicate is retained.

    Raises:
        ValueError: If the input DataFrame is empty or missing required columns.

    Note:
        This function identifies and removes duplicate job listings based on the specified columns. If multiple duplicates exist for a specific job, only the latest occurrence is kept.
    """
    # Check if there are any duplicates based on 'job_description', 'location', and 'job_title'
    has_duplicates = data.duplicated(subset=['job_description', 'search_location', 'job_title'], keep=False).any()
    output = pd.DataFrame()
    
    if has_duplicates:
        print("There are duplicate values based on 'job_description', 'search_location', and 'job_title' columns.")
        
        # Below code is only if you want to inspect the duplicated entries  
        # Filter to include only rows with duplicates based on all three columns and sort by 'job_description'
        #output = data[data.duplicated(subset=['job_description', 'search_location', 'job_title'], keep=False)]
        #output = output.sort_values(by=['job_description', 'search_location', 'job_title']).reset_index(drop=True)
        # Display the duplicates
        #print(output)
        
        # Remove duplicates and keep only the last occurrence
        output = data.drop_duplicates(subset=['job_description', 'search_location', 'job_title'], keep='last').reset_index(drop=True)
    else:
        print("No duplicates found based on 'job_description', 'search_location', and 'job_title'.")
        output = data 
    print(f'Size before: {data.size}. Size after removing duplicates: {output.size}')
    return output

def desc_categorical(data):
    """
    Function for describing categorical data. 
    Prints value counts for categorical columns in the given DataFrame.
    Identifies string and object columns, excluding 'job_description' and 'job_link' columns. 
    """
    # Exclude these 
    string_columns = data.select_dtypes(include='string').drop(columns='job_description') # Skip job description! 
    object_columns = data.select_dtypes(include='object').drop(columns='job_link')

    # Loop through the columns and print value counts
    for col in string_columns.columns:
        print(f"Value counts for column: {col}\n{string_columns[col].value_counts()}\n")
    for col in object_columns.columns:
        print(f"Value counts for column: {col}\n{object_columns[col].value_counts()}\n")

####### EXTRACT SALARY INFO ####### 

def convert_salary(value):
    # Converts salary strings with thousand separators or decimal points into a float.
    return float(value.replace('\xa0', '').replace(' ', '').replace(',', '').replace('.', '').replace('..', '.'))

def convert_salary_to_monthly(row, salary_column):
    """
    Converts a salary value to a monthly equivalent based on the specified time period. 
    Extracts the 'time_period' from the given row and uses a mapping dictionary to determine the appropriate conversion factor.
    If the 'time_period' is a valid string, the salary is multiplied by the conversion factor to obtain the monthly equivalent.

    Args:
        row: A Pandas Series representing a row of the DataFrame.
        salary_column: The name of the column containing the salary value.

    Returns:
        The monthly equivalent of the salary, or NaN if the time period is invalid or not recognized.
    """
    # Dictionary to map time periods (in different languages) to their monthly conversion factor
    time_period_map = {
        'hour': 160, 'ora': 160, 'heure': 160,
        'year': 1/12, 'anno': 1/12, 'par an': 1/12,
        'week': 4, 'settimana': 4, 'semaine': 4,
        'day': 20, 'giorno': 20, 'jour': 20,
        'month': 1, 'mese': 1, 'mois': 1, 'månad': 1
    }
    
    time_period = row['time_period']
    
    # Check if 'time_period' is a valid string and map it to conversion factor, otherwise return NaN
    if isinstance(time_period, str):
        time_period = time_period.lower()
        return row[salary_column] * time_period_map.get(time_period, np.nan)
    
    return np.nan
    
def clean_columns(data):
    """
    Cleans and formats columns in the given DataFrame.

    Args:
        data: The input DataFrame.

    Returns:
        The cleaned DataFrame with the following modifications:
            - Removes '+' signs from 'search_keyword' and 'search_location'.
            - Removes newline characters from 'job_description'.
            - Extracts numeric values from 'salary' and creates 'salary_num_low' and 'salary_num_high' columns.
            - Extracts time period from 'salary' and stores it in the 'time_period' column.
    """
    # Remove + signs and replace them with spaces in 'search_keyword' and 'search_location'
    data[['search_keyword', 'search_location']] = data[['search_keyword', 'search_location']].replace({r'\+': ' '}, regex=True)
    
    # Remove all newline characters from 'job_description'
    data['job_description'] = data['job_description'].replace({r'\n': ' '}, regex=True)
    
    # Extract salary numbers using regex
    # This regex captures numbers with commas, spaces, and periods, handling both American and European formats
    data['salary'] = data['salary'].astype(str)
    data['salary_num'] = data['salary'].apply(lambda x: re.findall(r'\d{1,3}(?:[,\s]\d{3})*(?:\.\d+)?', x))
    
    # Replace empty lists with NaN in 'salary_num'
    data['salary_num'] = data['salary_num'].apply(lambda x: x if x else np.nan)
    
    # Create 'salary_num_low' and 'salary_num_high' by extracting and cleaning the numbers
    # If there is only one number put it in both low and high column
    data['salary_num_low'] = data['salary_num'].apply(lambda x: convert_salary(x[0]) if isinstance(x, list) and len(x) > 0 else np.nan)
    data['salary_num_high'] = data['salary_num'].apply(lambda x: convert_salary(x[0]) if isinstance(x, list) and len(x) == 1 else convert_salary(x[1]) if isinstance(x, list) and len(x) > 1 else np.nan)
    # The error occurs for salary_num_high
    
    # Extract time period from 'salary' column using regex
    # par an since 'an' is an English word 
    data['time_period'] = data['salary'].str.extract(r'(hour|year|month|week|day|ora|anno|mese|settimana|giorno|heure|par an|mois|semaine|jour|månad)')

    return data

def apply_salary_conversion(df, currency):
    # Function to apply salary conversion for min and max salary
    df['min_salary_month'] = df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_low'), axis=1)
    df['max_salary_month'] = df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_high'), axis=1)
    df['currency'] = currency  # Add currency column
    return df

def clean_and_add_currency_and_salaries(df, currency):
    # Function to clean DataFrames, add a currency column, and calculate salary per month
    cleaned_df = clean_columns(df)  # Clean the DataFrame
    cleaned_df['currency'] = currency  # Add currency column
    # Calculate min and max salary per month
    cleaned_df['min_salary_month'] = cleaned_df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_low'), axis=1)
    cleaned_df['max_salary_month'] = cleaned_df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_high'), axis=1)
    return cleaned_df

def get_exchange_rate(base_currency, target_currency):
    """
    This function makes a request to the Frankfurter.app API to retrieve current
    exchange rate. 

    Args:
        base_currency (str): The currency code of the base currency (e.g., 'SEK', 'USD').
        target_currency (str): The currency code of the target currency (e.g., 'EUR').

    Returns:
        float: The exchange rate from base_currency to target_currency if successful, None otherwise.'
    """

    url = "https://api.frankfurter.app/latest"
    params = {
        'from': base_currency,
        'to': target_currency
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        # Return the exchange rate
        return data['rates'][target_currency]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate from {base_currency} to {target_currency}: {e}")
        return None

####### EXTRACT INFO FROM TEXT: JOB DESCRIPTIONS, INTERVIEW PROCESS, SOFTWARE KEYWORDS #######  

def extract_keywords(df, country, language):
    """
    Extracts and returns the most common keywords from job descriptions in a specified country and language.

    Args:
        df: The DataFrame containing job descriptions and other relevant columns.
        country: The country to filter the data by.
        language: The language of the job descriptions.

    Returns:
        A tuple containing:
            1. A list of the top 10 most common keywords.
            2. A list of all extracted tokens.
    """
    
    # Always include English stopwords
    stop_words = set(stopwords.words('english'))

    # Add additional stopwords based on the specified language
    if language == 'french':
        stop_words.update(stopwords.words('french'))
    elif language == 'italian':
        stop_words.update(stopwords.words('italian'))
    elif language == 'swedish':
        stop_words.update(stopwords.words('swedish'))
    elif language == 'english':
        # English stopwords are already included at the top
        pass
    else:
        raise ValueError("Unsupported language.")

    # Filter the DataFrame for the specified country
    df_country = df[df['country'] == country].copy()  # Create a copy to avoid SettingWithCopyWarning

    # Use .loc to assign new columns
    df_country.loc[:, 'cleaned_description'] = df_country['job_description'].apply(preprocess_text)
    #df_country.loc[:, 'tokens'] = df_country['cleaned_description'].apply(tokenize_and_filter)
    df_country.loc[:, 'tokens'] = df_country['cleaned_description'].apply(lambda text: tokenize_and_filter(text, stop_words))

    # Flatten the list of tokens and count frequencies
    all_tokens = [token for sublist in df_country['tokens'] for token in sublist]
    word_counts = Counter(all_tokens)

    # Get the top 10 keywords
    common_keywords = word_counts.most_common(10)  
    return (common_keywords, all_tokens)

def count_keywords(df, country, software_keywords):
    """
    Counts the occurrences of keywords in job descriptions for a specific country and categorizes them.

    Args:
        df: The DataFrame containing job descriptions and search keywords.
        country: The country to filter the data by.
        software_keywords: A dictionary mapping categories to lists of keywords.

    Returns:
        A DataFrame with columns for category, keyword, count, associated search keyword, and country.
    """
    # Prepare the DataFrame list to store individual entries
    data = []

    # Filter DataFrame by country
    filtered_df = df[df['country'] == country]
    
    # Flatten the keywords into a single list with their categories
    category_keywords = [(category, keyword) for category, keywords in software_keywords.items() for keyword in keywords]

    for index, row in filtered_df.iterrows():
        job_description = row['job_description'].lower()  # Access job description
        search_keyword = row['search_keyword']  # Access associated search keyword
        
        for category, keyword in category_keywords:
            count = job_description.count(keyword)
            if count > 0:  # Only record non-zero counts
                data.append({
                    'Category': category,
                    'Keyword': keyword,
                    'Count': count,
                    'Search Keyword': search_keyword,
                    'Country': country  
                })

    # Create a df from the collected data
    result_df = pd.DataFrame(data)

    # Group by relevant columns and sum the counts
    result_df = result_df.groupby(['Category', 'Keyword', 'Search Keyword', 'Country'], as_index=False).sum()

    return result_df


def extract_stage_text(job_desc, stage_pattern, context_window=100):
    """
    Extracts text related to the interview process from a job description.

    Args:
        job_desc: The text of the job description.
        stage_pattern: A string or raw string pattern representing an interview stage (e.g., "phone interview").
        context_window: The number of characters to capture around the matched stage pattern (default: 100).

    Returns:
        A string containing the extracted text surrounding the stage pattern within the interview process context, 
        or None if no match is found.
    """
    # Define the context pattern as a constant here
    context_pattern = r'recruitment process|interview process'

    # First, find the location of the context pattern
    context_match = re.search(context_pattern, job_desc, re.IGNORECASE)
    
    if context_match:
        # Narrow down the text to start after the context pattern match
        context_start = context_match.end()
        text_after_context = job_desc[context_start:]
        
        # Now, search for the stage pattern within this limited text
        stage_match = re.search(stage_pattern, text_after_context, re.IGNORECASE)
        
        if stage_match:
            # Calculate the adjusted start and end based on `text_after_context`
            start = max(0, stage_match.start() - 20)
            end = min(len(text_after_context), stage_match.end() + context_window)
            
            # Print the extracted text
            extracted_text = text_after_context[start:end].strip()
            #print("----Extracted Text Around Stage Pattern----")
            #print(extracted_text)
            return extracted_text  # Return the extracted text
            
    return None  # Return None if no match is found
    
def extract_interview_details(df, stages):
    """
    Extracts detailed information about interview stages from job descriptions and creates two DataFrames.

    Args:
        df: The DataFrame containing job descriptions and other relevant information.
        stages: Dictionary with fefined patterns for each interview stage.
    
    Returns:
        A tuple of two DataFrames:
        1. Detailed text DataFrame: Contains extracted text for each interview stage, along with job ID, title, and link.
        2. Boolean indicator DataFrame: Indicates the presence of each interview stage with True/False values.
    """
    interview_info = []
    interview_flags = []

    for _, row in df.iterrows():
        job_desc = row['job_description']
        
        # Store detailed text and flags for each stage in dictionaries
        details = {
            'job_id': row['job_id'],
            'job_title': row['job_title'],     # Add job title
            'job_link': row['job_link']        # Add job link or other useful identifiers
        }
        flags = {
            'job_id': row['job_id'],
            'job_title': row['job_title'],
            'job_link': row['job_link']
        }
        
        for stage, pattern in stages.items():
            extracted_text = extract_stage_text(job_desc, pattern)
            details[f'{stage}_text'] = extracted_text
            flags[stage] = bool(extracted_text)
        
        interview_info.append(details)
        interview_flags.append(flags)

    # Convert the lists of dictionaries into DataFrames
    interview_info_df = pd.DataFrame(interview_info)
    interview_flags_df = pd.DataFrame(interview_flags)

    return interview_info_df, interview_flags_df