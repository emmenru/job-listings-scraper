import re
import requests
import numpy as np

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
    # Is this even used?
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