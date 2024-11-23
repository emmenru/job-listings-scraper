import re
import requests
import numpy as np
import pandas as pd

"""
def convert_salary(value):
    # Converts salary strings with thousand separators or decimal points into a float.
    return float(value.replace('\xa0', '').replace(' ', '').replace(',', '').replace('.', '').replace('..', '.'))
"""


def get_time_keywords(language):
    """Get time unit keywords for different languages"""
    keywords = {
        'english': {
            'year': 'year|annual',
            'month': 'month',
            'hour': 'hour',
            'week': 'week'
        },
        'french': {
            'year': r'par\s*an|annuel|année',  
            'month': r'par\s*mois|mensuel',  
            'hour': r'par\s*heure|horaire',
            'week': r'par\s*semaine|hebdomadaire'
        },
        'italian': {
            'year': 'anno|annuale',
            'month': 'mese|mensile',
            'hour': 'ora|orario',
            'week': 'settimana|settimanale'
        },
        'swedish': {
            'year': 'år|årlig',
            'month': 'månad|mån',
            'hour': 'timme|tim|/h',
            'week': 'vecka'
        }
    }
    return keywords.get(language.lower(), keywords['english'])  # default to English if language not found


def convert_salary_to_monthly(df, salary_column, time_unit_column):
    """
    Vectorized function to convert salary values to monthly equivalents based on time periods.
    
    Args:
        df: A pandas DataFrame containing the salary and time_period columns
        salary_column: The name of the column containing the salary values
    
    Returns:
        A pandas Series containing the monthly equivalent salaries
    """
    # Dictionary to map time periods to their monthly conversion factor
    time_period_map = {
        'hour': 160, 'ora': 160, 'heure': 160,
        'year': 1/12, 'anno': 1/12, 'par an': 1/12,
        'week': 4, 'settimana': 4, 'semaine': 4,
        'day': 20, 'giorno': 20, 'jour': 20,
        'month': 1, 'mese': 1, 'mois': 1, 'månad': 1
    }
    
    # Create a categorical type with the mapping dictionary keys
    period_categories = list(time_period_map.keys())
    
    # Convert time_period column to lowercase and categorical type
    time_periods = pd.Categorical(
        df[time_unit_column].str.lower(),
        categories=period_categories,
        ordered=False
    )
    
    # Create a mapping Series for faster lookup
    conversion_factors = pd.Series(time_period_map)
    
    # Map the conversion factors to the time periods
    factors = pd.Series(time_periods).map(conversion_factors)
    
    # Multiply salary by conversion factors
    return df[salary_column] * factors

def parse_french_salary(s, dtype=float):
    """Parse French salary strings to extract min and max values."""
    number_pattern = r'[\d\s]+(?:,\d+)?'  # Matches numbers with spaces or commas

    def extract_numbers(row):
        numbers = re.findall(number_pattern, row)
        # Clean and convert numbers to float, handling all spaces (regular and non-breaking)
        numbers = [
            float(num.replace('\xa0', '').replace(' ', '').replace(',', '.'))
            for num in numbers if num.strip()  # Ensure the number is not empty
        ]
        # Return min and max, or duplicate if only one number exists
        if not numbers:
            return [None, None]  # Handle cases with no valid numbers
        return [numbers[0], numbers[1] if len(numbers) >= 2 else numbers[0]]

    # Apply extraction logic to each row
    numbers = s.apply(extract_numbers)
    
    return pd.DataFrame({
        'min_salary': numbers.apply(lambda x: x[0] if x else None),
        'max_salary': numbers.apply(lambda x: x[1] if x else None)
    })
    
def parse_salary_column(df, column_name='salary', languages=['english'], country='USA'):
    """
    Parse salary information from text data, extracting minimum and maximum salaries,
    currency, and time units. Handles different number formats based on country.
    """
    df = df.copy()
    
    # Initialize with pd.NA and specify dtypes
    df['min_salary'] = pd.Series(dtype='Float64')  # capital F allows NA
    df['max_salary'] = pd.Series(dtype='Float64')
    df['currency'] = pd.Series(dtype='string')
    df['time_unit'] = pd.Series(dtype='string')
    
    # Add duration pattern to exclude
    duration_pattern = r'durée jusqu\'à \d+\s*mois'
    
    # Modified mask to exclude duration entries
    valid_mask = (df[column_name].notna() & 
                 df[column_name].str.contains(r'\d', na=False) & 
                 ~df[column_name].str.contains(duration_pattern, case=False, na=False))
    
    if not valid_mask.any():
        return df
        
    s = df.loc[valid_mask, column_name].str.lower()

    # Parse salary values based on country format
    if country == 'Sweden':
        number_pattern = r'[\d]+\s*[\d]*'
        numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]]) 
        min_vals = numbers.str[0].str.replace(r'\s+', '', regex=True)
        max_vals = numbers.str[1].str.replace(r'\s+', '', regex=True)
        df.loc[valid_mask, 'min_salary'] = pd.to_numeric(min_vals, errors='coerce')
        df.loc[valid_mask, 'max_salary'] = pd.to_numeric(max_vals, errors='coerce')
        print(df.loc[valid_mask, ['min_salary', 'max_salary']])

    elif country == 'France':
        salary_data = parse_french_salary(s)
        df.loc[valid_mask, 'min_salary'] = salary_data['min_salary']
        df.loc[valid_mask, 'max_salary'] = salary_data['max_salary']
        print(df.loc[valid_mask, ['min_salary', 'max_salary']])
    
    elif country == 'Italy':
        s = s.apply(lambda x: re.sub(r'(\d+)\.(\d{3})', r'\1\2', str(x)))  # Remove dots first
        numbers = s.str.findall(r'\d+').apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
        df.loc[valid_mask, 'min_salary'] = pd.to_numeric(numbers.str[0], errors='coerce')
        df.loc[valid_mask, 'max_salary'] = pd.to_numeric(numbers.str[1], errors='coerce')
        print(df.loc[valid_mask, ['min_salary', 'max_salary']])

    else:  # USA 
        number_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?|\d+)'
        numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]]) 
        df.loc[valid_mask, 'min_salary'] = pd.to_numeric(numbers.str[0].str.replace(',', ''), errors='coerce')
        df.loc[valid_mask, 'max_salary'] = pd.to_numeric(numbers.str[1].str.replace(',', ''), errors='coerce')  
        print(df.loc[valid_mask, ['min_salary', 'max_salary']])
    
    # Currency detection
    df.loc[valid_mask, 'currency'] = np.where(s.str.contains('kr|kronor|sek', case=False), 'sek',
                                   np.where(s.str.contains('€|euro', case=False), 'euro',
                                   np.where(s.str.contains('$|dollar', case=False), 'dollar', None)))

    # Time patterns
    time_patterns = get_time_keywords(languages[0])
    if len(languages)>1:
        time_patterns_2 = get_time_keywords(languages[1])
        for key in time_patterns:
            time_patterns[key] = f'{time_patterns[key]}|{time_patterns_2[key]}'

    conditions = [s.str.contains(pattern) for pattern in time_patterns.values()]
    choices = list(time_patterns.keys())
    df.loc[valid_mask, 'time_unit'] = np.select(conditions, choices, default=None)

    # Clean up null values
    columns_to_check = ['min_salary', 'max_salary', 'currency', 'time_unit']
    for col in columns_to_check:
        df[col] = df[col].replace([np.nan, None], pd.NA)
   
    return df

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