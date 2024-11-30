import re
import requests
import numpy as np
import pandas as pd

from utils.dictionaries import TIME_KEYWORDS, TIME_PERIOD_MAP

def get_time_keywords(language: str, time_keyword_dict: dict[str, dict[str, str]]) -> dict[str, str]:
    '''Get time unit keywords for different languages.'''
    return TIME_KEYWORDS.get(language.lower(), TIME_KEYWORDS['english'])
    
def convert_salary_to_monthly(df: pd.DataFrame, salary_column: str, time_unit_column: str) -> pd.Series:
    '''
    Vectorized function to convert salary values to monthly equivalents based on time periods.
    
    Args:
        df: A pandas DataFrame containing the salary and time_period columns
        salary_column: The name of the column containing the salary values
    
    Returns:
        A pandas Series containing the monthly equivalent salaries
    '''
    
    # Create a categorical type with the mapping dictionary keys
    period_categories = list(TIME_PERIOD_MAP.keys())
    
    # Convert time_period column to lowercase and categorical type
    time_periods = pd.Categorical(
        df[time_unit_column].str.lower(),
        categories=period_categories,
        ordered=False
    )
    
    # Create a mapping Series for faster lookup
    conversion_factors = pd.Series(TIME_PERIOD_MAP)
    
    # Convert time units to lowercase and map directly to conversion factors (preserve NAs)
    factors = df[time_unit_column].str.lower().map(TIME_PERIOD_MAP)

    # Multiply salary by conversion factors
    return df[salary_column] * factors

def parse_french_salary(s: pd.Series) -> pd.DataFrame:
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


def parse_swedish_salary(s: pd.Series) -> pd.DataFrame:
    number_pattern = r'[\d]+\s*[\d]*'
    numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
    return pd.DataFrame({
        'min_salary': pd.to_numeric(numbers.str[0].str.replace(r'\s+', '', regex=True), errors='coerce'),
        'max_salary': pd.to_numeric(numbers.str[1].str.replace(r'\s+', '', regex=True), errors='coerce'),
        'currency': np.where(s.str.contains('kr|kronor|sek', case=False), 'sek', None)
    })


def parse_italian_salary(s: pd.Series) -> pd.DataFrame:
    s = s.apply(lambda x: re.sub(r'(\d+)\.(\d{3})', r'\1\2', str(x)))  # Remove dots
    numbers = s.str.findall(r'\d+').apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
    return pd.DataFrame({
        'min_salary': pd.to_numeric(numbers.str[0], errors='coerce'),
        'max_salary': pd.to_numeric(numbers.str[1], errors='coerce'),
        'currency': np.where(s.str.contains('€|euro', case=False), 'euro', None)
    })


def parse_usa_salary(s: pd.Series) -> pd.DataFrame:
    number_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?|\d+)'
    numbers = s.str.findall(number_pattern).apply(lambda x: [x[0], x[1] if len(x) >= 2 else x[0]])
    return pd.DataFrame({
        'min_salary': pd.to_numeric(numbers.str[0].str.replace(',', ''), errors='coerce'),
        'max_salary': pd.to_numeric(numbers.str[1].str.replace(',', ''), errors='coerce'),
        'currency': np.where(s.str.contains('$|dollar', case=False), 'dollar', None)
    })


def parse_salary_column(df: pd.DataFrame, column_name: str = 'salary', languages: list[str] = ['english'], country: str = 'USA') -> pd.DataFrame:
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
    time_patterns = get_time_keywords(languages[0], TIME_KEYWORDS)
    if len(languages) > 1:
        time_patterns_2 = get_time_keywords(languages[1], TIME_KEYWORDS)
        for key in time_patterns:
            time_patterns[key] = f'{time_patterns[key]}|{time_patterns_2[key]}'

    conditions = [s.str.contains(pattern) for pattern in time_patterns.values()]
    choices = list(time_patterns.keys())
    df.loc[valid_mask, 'time_unit'] = np.select(conditions, choices, default=None)

    # Clean up null values
    for col in ['min_salary', 'max_salary', 'currency', 'time_unit']:
        df[col] = df[col].replace([np.nan, None], pd.NA)
        
    return df

def get_exchange_rate(base_currency: str, target_currency: str) -> float:
    '''Retrieve current exchange rate from Frankfurter.app API.'''
    url = "https://api.frankfurter.app/latest"
    params = {
        'from': base_currency.upper(),
        'to': target_currency.upper()
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['rates'][target_currency.upper()]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate from {base_currency} to {target_currency}: {e}")
        return None

def convert_to_eur(df: pd.DataFrame, exchange_rates: dict[str, float]) -> pd.DataFrame:
    '''Convert salary columns to EUR using provided exchange rates.'''
    df = df.copy()
    
    # Simple mapping for our three known categories
    currency_mapping = {
        'dollar': exchange_rates['USD'],
        'euro': exchange_rates['EUR'],
        'sek': exchange_rates['SEK']
    }
    
    # Create a series of rates matching the df's currency column
    # Replace NA with 1 temporarily for the multiplication
    rates = df['currency'].map(currency_mapping).fillna(np.nan)
    
    # Print debug information
    print("\nDebug Information:")
    print("Currency mapping:", currency_mapping)
    print("\nCurrency value counts:", df['currency'].value_counts(dropna=False))
    
    # Convert salaries
    # Only convert where we have both a valid rate and a valid salary
    mask = rates.notna() & df['min_salary_monthly'].notna()
    df['min_salary_month_EUR'] = pd.NA
    df.loc[mask, 'min_salary_month_EUR'] = (
        df.loc[mask, 'min_salary_monthly'] * rates[mask]
    )
    
    mask = rates.notna() & df['max_salary_monthly'].notna()
    df['max_salary_month_EUR'] = pd.NA
    df.loc[mask, 'max_salary_month_EUR'] = (
        df.loc[mask, 'max_salary_monthly'] * rates[mask]
    )
    
    return df

def process_salaries(df: pd.DataFrame) -> pd.DataFrame:
    '''Process all salaries and convert them to EUR.'''
    # Initialize exchange rates
    exchange_rates = {
        'SEK': get_exchange_rate('SEK', 'EUR'),
        'USD': get_exchange_rate('USD', 'EUR'),
        'EUR': 1
    }
    
    print("Exchange rates:", exchange_rates)
    
    # Convert salaries to EUR
    df_converted = convert_to_eur(df, exchange_rates)
    
    # Show sample results for each currency type
    print("\nSample conversions for each currency:")
    for curr in ['dollar', 'euro', 'sek']:
        print(f"\n{curr.upper()} conversions:")
        sample = df_converted[df_converted['currency'] == curr][
            ['currency', 'min_salary_monthly', 'max_salary_monthly', 
             'min_salary_month_EUR', 'max_salary_month_EUR']].head(2)
        print(sample)
    
    # Print summary of conversion results
    print("\nConversion summary:")
    print("Total rows:", len(df_converted))
    print("Rows with min salary in EUR:", df_converted['min_salary_month_EUR'].notna().sum())
    print("Rows with max salary in EUR:", df_converted['max_salary_month_EUR'].notna().sum())
    
    return df_converted

def update_salary_data(df: pd.DataFrame) -> pd.DataFrame:
   """Update salary-related columns in the DataFrame for each country."""
   df = df.copy()
   
   for country in df['country'].unique():
       mask = df['country'] == country
       unique_langs = df[mask]['language'].unique().tolist()
       
       print('*' * 30, f'Retrieving salaries for {country}:', f'Languages: {unique_langs}', sep='\n')
       
       result = parse_salary_column(
           df[mask], 
           languages=unique_langs, 
           country=country
       )
       
       print(f'Rows changed for {country}: {result.shape[0]}. Original rows retrieved: {df[mask].shape[0]}')
       
       if result.shape[0] != df[mask].shape[0]:
           print(f"Warning: Size mismatch for {country}. Expected {df[mask].size}, got {result.size}")
           return df
           
       columns_to_update = ['min_salary', 'max_salary', 'currency', 'time_unit']
       df.loc[mask, columns_to_update] = result[columns_to_update]
       print('*' * 30 + '\n')
   
   return df
