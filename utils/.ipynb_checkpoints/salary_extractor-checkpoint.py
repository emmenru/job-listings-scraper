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
            'year': 'an|annuel|année',
            'month': 'mois|mensuel',
            'hour': 'heure|horaire',
            'week': 'semaine|hebdomadaire'
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

def parse_salary_column(df, column_name='salary', languages=['english'], country='USA'):
    df = df.copy()
    df['min_salary'] = np.nan
    df['max_salary'] = np.nan
    df['currency'] = None
    df['time_unit'] = None
    
    # Create combined mask
    valid_mask = df[column_name].notna() & df[column_name].str.contains(r'\d', na=False)
    if not valid_mask.any():
        return df
        
    s = df.loc[valid_mask, column_name].str.lower()
    
    if country in ['Sweden', 'France']:
        number_pattern = r'[\d]+\s*[\d]*'
        numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]]) 
        print("Numbers found: ")
        print(numbers)
        min_vals = numbers.str[0].str.replace(r'\s+', '', regex=True)
        max_vals = numbers.str[1].str.replace(r'\s+', '', regex=True)
        df.loc[valid_mask, 'min_salary'] = pd.to_numeric(min_vals, errors='coerce')
        df.loc[valid_mask, 'max_salary'] = pd.to_numeric(max_vals, errors='coerce')
        print("--------------------------- ")
        print("After assignment:\n")
        print(df.loc[valid_mask, ['min_salary', 'max_salary']])
    elif country == 'Italy':
        s = s.apply(lambda x: re.sub(r'(\d+)\.(\d{3})', r'\1\2', str(x)))  # Remove dots first
        numbers = s.str.findall(r'\d+').apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
        print("\nNumbers found:")
        print(numbers)
        df.loc[valid_mask, 'min_salary'] = pd.to_numeric(numbers.str[0], errors='coerce')
        df.loc[valid_mask, 'max_salary'] = pd.to_numeric(numbers.str[1], errors='coerce')
    else:
        number_pattern = number_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?|\d+)'
        numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]]) 
        print("\nNumbers found:")
        print(numbers)
        df.loc[valid_mask, 'min_salary'] = pd.to_numeric(numbers.str[0].str.replace(',', ''), errors='coerce')
        df.loc[valid_mask, 'max_salary'] = pd.to_numeric(numbers.str[1].str.replace(',', ''), errors='coerce')  

    df.loc[valid_mask, 'currency'] = np.where(s.str.contains('$|dollar'), 'dollar',
                                    np.where(s.str.contains('€|euro'), 'euro',
                                    np.where(s.str.contains('kr|kronor|sek'), 'sek', None)))
    
    time_patterns = get_time_keywords(languages[0])
    if len(languages)>1:
        time_patterns_2 = get_time_keywords(languages[1])
        for key in time_patterns:
            time_patterns[key] = f"{time_patterns[key]}|{time_patterns_2[key]}"
    
    conditions = [s.str.contains(pattern) for pattern in time_patterns.values()]
    choices = list(time_patterns.keys())
    df.loc[valid_mask, 'time_unit'] = np.select(conditions, choices, default=None)
    
    return df
    

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

def apply_salary_conversion(df, currency):
    # Is this even used?
    # Function to apply salary conversion for min and max salary
    df['min_salary_month'] = df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_low'), axis=1)
    df['max_salary_month'] = df.apply(lambda row: convert_salary_to_monthly(row, 'salary_num_high'), axis=1)
    df['currency'] = currency  # Add currency column
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