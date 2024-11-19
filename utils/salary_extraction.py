import re
import pandas as pd
import numpy as np

EXCLUDED_PATTERNS = {
   'usa': [
       r'id \d+',
       r'us-\d+', 
       r'\d+\.?\d*\s*billion',
       r'\d+ pay detail',
       r'child low \d+',
       r'retirement plan like \d+ dollar-for-dollar',
       r'\d+ per-capita healthcare',
       r' leave \d+'
   ],
   'sweden': [
       r'avdrag|castra|grundades \d+',
       r'\d+\s*(år|miljarder|uppdrag)',  # Exclude entries with 'nummer år' och 'nummer miljarder'
       r'(health|wellness) (contribution|allowance)\s*(sek\s*)?\d+',
       r'\b\d{2}-\d{2}-\d{4}\b', # Swedish dates
       r'tjänstepension itp1\s*\d+', 
       r'\d+\s*dagars semester'
    ]
}

# Base English terms (used across all countries, since some ads are in English)
ENGLISH_TERMS = "salary|compensation|pay|wage"

# Country-specific terms, merged with English terms where needed
SALARY_TERMS = {
    'usa': [ENGLISH_TERMS],
    'france': [ENGLISH_TERMS],
    'sweden': [f"lön|betalning|{ENGLISH_TERMS}"],  # Swedish terms + English terms
    'italy': [ENGLISH_TERMS]
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
    # This should change depending on language used 
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
    """
    Extract valid numeric values depending on country format.
    
    Args:
    - text (str): The input text containing numbers.
    - country (str): The country format ('usa' or 'sweden').

    Returns:
    - List[float]: A list of extracted numbers in float format.
    """
    if country == 'usa':   
        # US format: 300, 30,000, 30000.00, or 30k
        pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:k)?\b'
        return (
            pd.Series(re.findall(pattern, text))
            .dropna()
            .loc[lambda x: ~x.str.startswith('0') & ~x.str.contains('401')]
            .map(lambda x: float(x[:-1].replace(',', '')) * 1000 if x.endswith('k') 
                 else float(x.replace(',', '')))
            .tolist()
        )
    elif country == 'sweden': 
        # Swedish format: 300, 30 000, 30 000,00
        pattern = r'\b\d+(?:\s?\d{3})*(?:,\d+)?\b'
        return (
            pd.Series(re.findall(pattern, text))
            .dropna()
            .map(lambda x: float(x.replace(' ', '').replace(',', '.')))
            .tolist()
        )
    else:
        raise ValueError("Unsupported country format.")
       
def detect_salary_magnitude_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """Detect rows with salary magnitude mismatch."""
    language = 'english'
    mask = pd.notna(df['min_salary']) & pd.notna(df['max_salary'])
    magnitude_diff = (df[mask]['max_salary'].astype(int).astype(str).str.len() - 
                     df[mask]['min_salary'].astype(int).astype(str).str.len()).abs()
    
    return df[mask & (magnitude_diff >= 2)][['min_salary', 'max_salary', 'context_string']]
    
def extract_salary_info(text: str, currencies: dict, country: str) -> pd.Series:
    """Extract salary information from text."""
    default_result = pd.Series({k: None for k in ['min_salary', 'max_salary', 'currency', 
                              'time_period', 'context_string']} | {'salary_extraction_success': False})
    
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
                
                if numbers := [n for n in extract_numbers(context, country) 
                             if n != 0 and not any(re.search(pat.replace(r'\d+', r'\d*\.?\d*'), context) 
                                                 for pat in EXCLUDED_PATTERNS.get(country.lower(), []))]: # Get specific excluded patterns for country 
                    return pd.Series({
                        'min_salary': min(numbers),
                        'max_salary': max(numbers),
                        'currency': currency_symbol,
                        'time_period': extract_time_unit(context),
                        'context_string': context,
                        'salary_extraction_success': True
                    })
    except Exception:
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