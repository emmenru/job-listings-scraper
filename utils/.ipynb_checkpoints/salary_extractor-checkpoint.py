import re
import requests
import numpy as np
import pandas as pd

def get_time_keywords(language):
    """Get time unit keywords for different languages"""
    keywords = {
        'english': {
            'day': 'day',
            'year': 'year|annual',
            'month': 'month',
            'hour': 'hour',
            'week': 'week'
        },
        'french': {
            'day': 'par jour',
            'year': r'par\s*an|annuel|année',  
            'month': r'par\s*mois|mensuel',  
            'hour': r'par\s*heure|horaire',
            'week': r'par\s*semaine|hebdomadaire'
        },
        'italian': {
            'day': 'al giorno',
            'year': 'anno|annuale',
            'month': 'mese|mensile',
            'hour': 'ora|orario',
            'week': 'settimana|settimanale'
        },
        'swedish': {
            'day': 'per dag',
            'year': 'år|årlig',
            'month': 'månad|mån',
            'hour': 'timme|tim|/h',
            'week': 'vecka'
        }
    }
    return keywords.get(language.lower(), keywords['english'])  # default to English if language not found


def convert_to_eur(df, exchange_rates):
    # Create a series of rates matching the df's currency column
    rates = df['currency'].map(exchange_rates).fillna(1)
    
    # Multiply only where salaries are not NA
    df['min_salary_month_EUR'] = df['min_salary_monthly'].multiply(rates, fill_value=pd.NA)
    df['max_salary_month_EUR'] = df['max_salary_monthly'].multiply(rates, fill_value=pd.NA)
    
    return df
    
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
        'hour': 160, 
        'year': 1/12, 
        'week': 4,
        'day': 20, 
        'month': 1,
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
    #factors = pd.Series(time_periods).map(conversion_factors)
    # Convert time units to lowercase and map directly to conversion factors
    # This will preserve NA values
    factors = df[time_unit_column].str.lower().map(time_period_map)

    # Multiply salary by conversion factors
    return df[salary_column] * factors

def parse_french_salary(s):
    number_pattern = r'[\d\s\xa0]+(?:,\d+)?'
    
    def extract_numbers(row):
        numbers = re.findall(number_pattern, row)
        numbers = [float(num.replace('\xa0', '').replace(' ', '').replace(',', '.')) for num in numbers if num.strip()]
        return [numbers[0], numbers[1] if len(numbers) >= 2 else numbers[0]]

    numbers = s.apply(extract_numbers)
    return pd.DataFrame({
        'min_salary': numbers.apply(lambda x: x[0] if x else None),
        'max_salary': numbers.apply(lambda x: x[1] if x else None),
        'currency': np.where(s.str.contains('€|euro', case=False), 'euro', None)
    })


def parse_swedish_salary(s):
    number_pattern = r'[\d]+\s*[\d]*'
    numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
    return pd.DataFrame({
        'min_salary': pd.to_numeric(numbers.str[0].str.replace(r'\s+', '', regex=True), errors='coerce'),
        'max_salary': pd.to_numeric(numbers.str[1].str.replace(r'\s+', '', regex=True), errors='coerce'),
        'currency': np.where(s.str.contains('kr|kronor|sek', case=False), 'sek', None)
    })


def parse_italian_salary(s):
    s = s.apply(lambda x: re.sub(r'(\d+)\.(\d{3})', r'\1\2', str(x)))  # Remove dots
    numbers = s.str.findall(r'\d+').apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
    return pd.DataFrame({
        'min_salary': pd.to_numeric(numbers.str[0], errors='coerce'),
        'max_salary': pd.to_numeric(numbers.str[1], errors='coerce'),
        'currency': np.where(s.str.contains('€|euro', case=False), 'euro', None)
    })


def parse_usa_salary(s):
    number_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?|\d+)'
    numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
    return pd.DataFrame({
        'min_salary': pd.to_numeric(numbers.str[0].str.replace(',', ''), errors='coerce'),
        'max_salary': pd.to_numeric(numbers.str[1].str.replace(',', ''), errors='coerce'),
        'currency': np.where(s.str.contains('$|dollar', case=False), 'dollar', None)
    })


def parse_salary_column(df, column_name='salary', languages=['english'], country='USA'):
    df = df.copy()

    # Initialize columns
    df['min_salary'] = pd.Series(dtype='Float64')
    df['max_salary'] = pd.Series(dtype='Float64')
    df['currency'] = pd.Series(dtype='string')
    df['time_unit'] = pd.Series(dtype='string')

    # Exclude invalid rows
    # this duration pattern should perhaps just remove the cases when there is only '6 month internship' for France?
    duration_pattern = r'durée jusqu\'à \d+\s*mois'
    valid_mask = (df[column_name].notna() & 
                  df[column_name].str.contains(r'\d', na=False) & 
                  ~df[column_name].str.contains(duration_pattern, case=False, na=False))
    if not valid_mask.any():
        return df

    s = df.loc[valid_mask, column_name].str.lower()

    # Country-specific parsing
    parse_funcs = {
        'France': parse_french_salary,
        'Sweden': parse_swedish_salary,
        'Italy': parse_italian_salary,
        'USA': parse_usa_salary
    }

    if country in parse_funcs:
        salary_data = parse_funcs[country](s)
        df.loc[valid_mask, ['min_salary', 'max_salary', 'currency']] = salary_data
        print(df.loc[valid_mask, ['min_salary', 'max_salary', 'currency']])  # Print output
    else:
        raise ValueError(f"Unsupported country: {country}")

    # Time patterns
    time_patterns = get_time_keywords(languages[0])
    if len(languages) > 1:
        time_patterns_2 = get_time_keywords(languages[1])
        for key in time_patterns:
            time_patterns[key] = f'{time_patterns[key]}|{time_patterns_2[key]}'

    conditions = [s.str.contains(pattern) for pattern in time_patterns.values()]
    choices = list(time_patterns.keys())
    df.loc[valid_mask, 'time_unit'] = np.select(conditions, choices, default=None)

    # Clean up null values
    for col in ['min_salary', 'max_salary', 'currency', 'time_unit']:
        df[col] = df[col].replace([np.nan, None], pd.NA)

    # After parsing and filling in data, set the categories for 'currency' and 'time_unit'
    #currency_categories = ['dollar', 'euro', 'sek']
    #time_unit_categories = ['year', 'month', 'week', 'hour', 'day']
    
    # Convert to categorical columns with predefined categories
    #df['currency'] = df['currency'].astype(pd.CategoricalDtype(categories=currency_categories, ordered=False))
    #df['time_unit'] = df['time_unit'].astype(pd.CategoricalDtype(categories=time_unit_categories, ordered=False))
    
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