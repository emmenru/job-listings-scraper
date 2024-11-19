import re
import pandas as pd
import numpy as np


# Base English terms (used across all countries, since some ads are in English)
ENGLISH_TERMS = "salary|compensation|pay|wage"

# Country-specific terms, merged with English terms where needed
SALARY_TERMS = {
    'usa': [ENGLISH_TERMS],
    'france': [ENGLISH_TERMS],
    'sweden': [f"lön|betalning|{ENGLISH_TERMS}"],  # Swedish terms + English terms
    'italy': [ENGLISH_TERMS]
}

NUMBER_PATTERNS = {
   'usa': r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:k)?\b',
   'sweden': r'\b\d+(?:\s?\d{3})*(?:,\d+)?\b',  
   'france': r'\b\d+(?:\.\d+)?(?:[,\d]*\d)?\b',
   'italy': r'\b\d+(?:\.?\d{3})*(?:,\d+)?\b'
}


def get_currency_patterns(country: str) -> dict:
    """ Get currency patterns for different countries."""
    euro_pattern = {'€': r'€', 'eur': r'\b(?:eur|euros?)\b'}
    patterns = {
        'sweden': {'kr': r'kr|kronor', 'sek': r'\b(?:sek)\b'},
        'france': euro_pattern,
        'italy': euro_pattern,
        'usa': {'$': r'\$', 'usd': r'\b(?:usd|dollars?)\b'}
    }
    return patterns.get(country.lower(), {})

def extract_time_unit(text: str) -> str:
    """Extract payment time unit from text."""
    if re.search(r'\b(?:per\s+hour|hourly|/hour|/hr|/h)\b', text, re.I):
        return 'per hour'
    if re.search(r'\b(?:per\s+week|weekly|/week|/wk|/w)\b', text, re.I):
        return 'per week'
    if re.search(r'\b(?:per\s+month|monthly|/month|/mo)\b', text, re.I):
        return 'per month'
    return 'per year'

def expand_context_for_numbers(text, start, end):
    """Expand context to include complete numbers at boundaries."""
    while start > 0 and re.match(r'[\d,\.]', text[start-1]):
        start -= 1
    while end < len(text) - 1 and re.match(r'[\d,\.]', text[end+1]):
        end += 1
    return start, end

def extract_numbers(text, country):
   if country not in NUMBER_PATTERNS:
       raise ValueError("Unsupported country format.")
       
   numbers = pd.Series(re.findall(NUMBER_PATTERNS[country], text)).dropna()
   
   if country == 'usa':
       numbers = numbers[~numbers.str.startswith('0')]
       return numbers.apply(lambda x: float(x[:-1].replace(',', '')) * 1000 if x.endswith('k') 
                          else float(x.replace(',', ''))).tolist()
   
   elif country == 'sweden':
       return numbers.apply(lambda x: float(x.replace(' ', '').replace(',', '.'))).tolist()
       
   elif country == 'france':
       return numbers.apply(lambda x: float(x.replace(' ', '').replace(',', ''))).tolist()
       
   else:  # italy
       return numbers.apply(lambda x: float(x.replace('.', '').replace(',', '.'))).tolist()
       
def detect_salary_magnitude_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """Detect rows with salary magnitude mismatch."""
    language = 'english'
    mask = pd.notna(df['min_salary']) & pd.notna(df['max_salary'])
    magnitude_diff = (df[mask]['max_salary'].astype(int).astype(str).str.len() - 
                     df[mask]['min_salary'].astype(int).astype(str).str.len()).abs()
    
    return df[mask & (magnitude_diff >= 2)][['min_salary', 'max_salary', 'context_string']]


def extract_salary_info(text: str, currencies: dict, country: str, language: str = 'english') -> pd.Series:
    SALARY_LIMITS = {
        'usa': {'hourly': (1, 1000), 'other': (15000, 1000000)},
        'france': {'hourly': (1, 500), 'other': (1000, 100000)},
        'sweden': {'hourly': (250, 10000), 'other': (6000, 1000000)},
        'italy': {'hourly': (1, 500), 'other': (15000, 500000)}
    }
    
    default_result = pd.Series({k: None for k in ['min_salary', 'max_salary', 'currency', 
                              'time_period', 'context_string', 'initial_numbers']} | {'salary_extraction_success': False})
    
    if not isinstance(text, str):
        return default_result
    
    try:
        text = text.lower()
        for currency_symbol, pattern in currencies.items():
            for match in re.finditer(pattern, text):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 40)
                start, end = expand_context_for_numbers(text, start, end)
                context = text[start:end]
                
                initial_numbers = extract_numbers(context, country)
                initial_numbers = [n for n in initial_numbers if n != 0]
                time_period = extract_time_unit(context)
                
                limits = SALARY_LIMITS[country.lower()]
                min_limit, max_limit = limits['hourly'] if time_period == 'per hour' else limits['other']
                
                numbers = [n for n in initial_numbers if min_limit <= n <= max_limit]
                
                print(f"initial numbers: {initial_numbers}")
                print(f"filtered numbers: {numbers}")
                
                if numbers:
                    return pd.Series({
                        'min_salary': min(numbers),
                        'max_salary': max(numbers),
                        'currency': currency_symbol,
                        'time_period': time_period,
                        'context_string': context,
                        'initial_numbers': initial_numbers,
                        'salary_extraction_success': True
                    })
    except Exception as e:
        print(f"Error: {e}")
        return default_result
    
    return default_result

def process_job_descriptions(df: pd.DataFrame, 
                           country: str, 
                           text_column: str = 'normalized_text') -> pd.DataFrame:
    """Extract salary information from job descriptions."""
    #salary_terms = salary_terms['usa']#'salary|compensation|pay|wage'
    # Access salary terms using .get() with a default value
    terms = SALARY_TERMS.get(country.lower(), [])
    print(terms)
    if not terms:
        raise ValueError(f"Salary terms not found for country: {country}")
    # Preprocess text once
    lowered_text = df[text_column].str.lower()
    lowered_country = df['country'].str.lower()
    
    mask = lowered_country.eq(country.lower()) & \
    lowered_text.str.contains(terms[0], na=False)

    df_out = df[mask].copy()
    
    if df_out.empty:
        return df_out
        
    df_out[['min_salary', 'max_salary', 'currency', 'time_period', 'context_string']] = None
    df_out['salary_extraction_success'] = False
    
    currencies = get_currency_patterns(country)
    df_out.update(lowered_text[mask].apply(lambda x: extract_salary_info(x, currencies, country)))
    
    return df_out