import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter
import requests 


# Ensure NLTK stopwords are downloaded (run this once)
nltk.download('stopwords')

# Helper functions 
    
def preprocess_text(text):
    # Remove punctuation and make lowercase
    return re.sub(r'[^\w\s]', '', text.lower())

def tokenize_and_filter(text, stop_words):
    # Tokenization: split text into words and remove stopwords
    tokens = text.split()
    return [word for word in tokens if word not in stop_words]
    
# High-level functions 

def merge_US_cities(cities, DATA_PATH):
    '''
    Merges job listings from multiple US cities into a single DataFrame.
    
    Parameters:
    - cities: List of city names (strings) to merge.

    Returns:
    - A DataFrame containing job listings from all specified US cities.
    '''
    
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

# unique() prints the unique values, nunique() prints the number of unique values
def check_duplicates(data):
    '''
    # The number of rows should be equal to the number of unique job links, etc 
    '''
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
    '''
    Checks for duplicate (same job description, location, and job title) in the DataFrame and keep only the latest entry if duplicate is identified. 
    
    Parameters:
    - data: The input DataFrame to check for duplicates.

    Returns:
    - A DataFrame containing with duplicates removed. 
    '''
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
    print(f'Size before: {data.size} Size after removing duplicates: {output.size}')
    return output

# Function for describing categorical data 

def desc_categorical(data):
    #print(data.columns)
    # Get frequency counts for each categorical column
    string_columns = data.select_dtypes(include='string').drop(columns='job_description') # Skip job description! 
    # Get frequency counts for the categorical columns with mixed data types (strings and numbers)
    object_columns = data.select_dtypes(include='object').drop(columns='job_link')

    # Loop through the columns and print value counts
    for col in string_columns.columns:
        print(f'Value counts for column: {col}\n{string_columns[col].value_counts()}\n')
    for col in object_columns.columns:
        print(f'Value counts for column: {col}\n{object_columns[col].value_counts()}\n')

# Functions for extracting salary information 


# Salary conversion function to handle both thousand separators and decimal points
def convert_salary(value):
    # Converts salary strings with thousand separators or decimal points into a float.
    return float(value.replace('\xa0', '').replace(' ', '').replace(',', '').replace('.', '').replace('..', '.'))

"""
New one 
def convert_salary(value):
    # Converts salary strings with thousand separators and decimal points into a float.
    cleaned_value = value.replace('\xa0', '')  # Remove non-breaking spaces
    cleaned_value = cleaned_value.replace(' ', '')  # Remove spaces (thousands separator)
    cleaned_value = cleaned_value.replace(',', '.')  # Replace comma with dot for decimal
    return float(cleaned_value)  # Convert to float
"""

# Format, clean, and fix columns for salary column 
def clean_columns(data):
    """
    Describe 
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
    # Hack for cases when there is a comma in the salary_num_high 
    # data['salary_num_high']
    
    # Extract time period from 'salary' column using regex
    # par an since 'an' is an English word 
    data['time_period'] = data['salary'].str.extract(r'(hour|year|month|week|day|ora|anno|mese|settimana|giorno|heure|par an|mois|semaine|jour|månad)')

    return data

def convert_salary_to_monthly(row, salary_column):
    '''
    Describe
    '''
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

# Function to apply salary conversion for min and max salary
def apply_salary_conversion(df, currency):
    df['min_salary_month'] = df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_low'), axis=1)
    df['max_salary_month'] = df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_high'), axis=1)
    df['currency'] = currency  # Add currency column
    return df

# Function to clean DataFrames, add a currency column, and calculate salary per month
def clean_and_add_currency_and_salaries(df, currency):
    cleaned_df = clean_columns(df)  # Clean the DataFrame
    cleaned_df['currency'] = currency  # Add currency column
    # Calculate min and max salary per month
    cleaned_df['min_salary_month'] = cleaned_df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_low'), axis=1)
    cleaned_df['max_salary_month'] = cleaned_df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_high'), axis=1)
    return cleaned_df

# Functions for extracting info from job descriptions 
def extract_keywords(df, country, language):
    '''
    Parameters:
    - df: DataFrame containing job descriptions and search keywords.
    - country: String representing the country to filter by.
    - language: language to filter by (to ensure correct stopwords are removed). 

    Returns:
    - A list with most common keywords? 
    '''
    
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

def plot_common_keywords(common_keywords, country):
    '''
    Plots the most common keywords from job descriptions.

    Parameters:
    - common_keywords: List of tuples (keyword, frequency).
    - country: Name of the country for labeling the plot.
    '''
    # Unzip the list of tuples into two lists: words and counts
    words, counts = zip(*common_keywords)

    # Create a bar plot
    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.bar(words, counts, color='skyblue')  # Bar plot
    plt.xlabel('Keywords', fontsize=14)  # Label for x-axis
    plt.ylabel('Frequency', fontsize=14)  # Label for y-axis
    plt.title(f'Most Common Keywords in Job Descriptions - {country}', fontsize=16)  # Title of the plot
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to make room for rotated labels
    plt.show()  # Display the plot

def count_keywords(df, country, software_keywords):
    '''
    Counts the occurrences of keywords in job descriptions by category and sub-category for a specific country,
    creating separate entries for each keyword and its associated search keyword.

    Parameters:
    - df: DataFrame containing job descriptions and search keywords.
    - country: String representing the country to filter by.

    Returns:
    - A DataFrame with categories, sub-categories, keyword counts, associated search keywords, and country.
    '''
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

# Extract information about interview process (when available)
def extract_stage_text(job_desc, stage_pattern, context_window=100):
    """
    Extracts text around a matched stage pattern in the job description,
    but only within text following a specified context pattern.
    
    Parameters:
    - job_desc: String containing the job description.
    - stage_pattern: String or raw string pattern to search for within the job description.
    - context_window: Integer indicating how many characters around the match to capture.
    
    Returns:
    - A string containing text surrounding the matched stage pattern after the context pattern, or None if no match is found.
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


def extract_interview_details(df):
    '''
    Extracts detailed information for all interview stages from job descriptions and creates both a DataFrame 
    with the extracted text and a Boolean indicator DataFrame.
    
    Parameters:
    - df: DataFrame containing job listings.
    
    Returns:
    - Tuple of DataFrames:
        - Detailed text DataFrame for each category.
        - Boolean indicator DataFrame showing True/False for the presence of each category.
    '''
    # Define patterns for each interview stage
   
    '''
    stages = {
    'phone_screening': r'phone screening|phone interview|screening call',
    'technical_screening': r'technical screening|technical interview|coding screen|technical phone screen',
    'case_study': r'case study|take-home assignment|business case',
    'coding_assessment': r'coding test|coding interview|programming test|technical assessment|live coding challenge|SQL test|Python test',
    'behavioral_interview': r'behavioral interview|cultural interview|HR interview|situational interview|behavioral questions',
    'on_site_interview': r'on-site interview|final round|in-person interview|panel interview',
    'presentation': r'project presentation|technical presentation'
  }
  '''
    stages = {
    'phone_screening': r'phone screening|phone interview|screening call|screening téléphonique|entrevue téléphonique|chiamata di screening|colloquio telefonico|telefonintervju',
    
    'technical_screening': r'technical screening|technical interview|coding screen|technical phone screen|évaluation technique|entrevue technique|codice di screening|screening tecnico|teknisk screening|teknisk intervju',

    'case_study': r'case study|take-home assignment|business case|étude de cas|assegnazione a casa|business case|caso studio|fallstudie|business case',

    'coding_assessment': r'coding test|coding interview|programming test|technical assessment|live coding challenge|SQL test|Python test|test di programmazione|intervista di programmazione|assessment tecnico|test SQL|test Python|kodningsprov|programmeringstest|teknisk bedömning',

    'behavioral_interview': r'behavioral interview|cultural interview|HR interview|situational interview|behavioral questions|entretien comportemental|entretien culturel|entrevue RH|entrevue situationnelle|domande comportamentali|colloquio comportamentale|HR-intervju|beteendefrågor',

    'on_site_interview': r'on-site interview|final round|in-person interview|panel interview|entrevue sur place|dernière ligne droite|entrevue en personne|entrevue en panel|intervista in sede|colloquio finale|colloquio in presenza|intervista di gruppo|panelintervju|slutintervju',

    'presentation': r'project presentation|technical presentation|présentation de projet|présentation technique|presentazione di progetto|presentazione tecnica'
}

    
    # Initialize lists to store extracted details and indicators
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

####### PLOTTING 

def plot_categorical(df, categorical_cols, top_n=10, horizontal=False):
    """
    Plots the distribution of specified categorical columns in a DataFrame.

    Parameters:
    - df: DataFrame containing the data.
    - categorical_cols: List of categorical columns to plot.
    - top_n: Integer specifying the number of top categories to display (default is 10).
    - horizontal: Boolean specifying if the plot should be horizontal (default is False).
    """
    for col in categorical_cols:
        plt.figure(figsize=(10, 6))
        
        # Count the top categories
        top_categories = df[col].value_counts().nlargest(top_n)
        
        # Create a count plot
        if horizontal:
            sns.countplot(data=df, y=col, order=top_categories.index)
        else:
            sns.countplot(data=df, x=col, order=top_categories.index)
        
        plt.title(f'Top {top_n} Categories of Column: {col}')
        
        plt.xticks(rotation=45)
        plt.show()

def plot_numerical(df, numerical_cols):
    """
    Performs univariate analysis for specified numerical columns in a DataFrame.
    
    Parameters:
    - df: DataFrame containing the data.
    - numerical_cols: List of numerical columns to analyze.
    """
    for col in numerical_cols:
        # Drop NaN values and check for valid data
        valid_data = df[col].dropna()
        
        # Check if there are enough values to plot
        # Summary statistics
        print(f"Summary statistics for {col}:")
        print(valid_data.describe())
        print("\n")
            
        # Boxplot
        plt.figure(figsize=(12, 6))
        sns.boxplot(x=valid_data)  # Use valid data for plotting
        plt.title(f'Boxplot of Column {col}')
        plt.xlabel(col)
        plt.grid()
        plt.show()

# Define the endpoint URL for multiple currency conversions
url = "https://api.frankfurter.app/latest"
params = {
    'from': 'EUR',       # Set the base currency to EUR
    'to': 'SEK,USD'      # List the target currencies separated by a comma
}

# Function to get exchange rate from one currency to another
def get_exchange_rate(base_currency, target_currency):
    """
    This function makes a request to the Frankfurter.app API to retrieve current
    exchange rate. 

    Parameters:
    base_currency (str): The currency code of the base currency (e.g., 'SEK', 'USD').
    target_currency (str): The currency code of the target currency (e.g., 'EUR').

    Returns:
    float: The exchange rate from base_currency to target_currency if successful,
           None otherwise.'
    
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
