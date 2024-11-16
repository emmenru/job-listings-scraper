import re
import requests
import numpy as np
import pandas as pd

"""
def convert_salary(value):
    # Converts salary strings with thousand separators or decimal points into a float.
    return float(value.replace('\xa0', '').replace(' ', '').replace(',', '').replace('.', '').replace('..', '.'))
"""


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