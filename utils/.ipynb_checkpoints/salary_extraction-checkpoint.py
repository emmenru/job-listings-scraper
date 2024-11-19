import re
import pandas as pd
import numpy as np

EXCLUDED_PATTERNS = [
    r'\d+\.?\d*\s*billion',
    r'id \d+',
    r'us-\d+',
    r'\d+ pay detail',
    r'child low \d+', 
    r'retirement plan like \d+ dollar-for-dollar', 
    r'\d+ per-capita healthcare',
    r' leave \d+'
]

def get_currency_patterns(country: str) -> dict:
    """
    Get currency patterns for different countries.
    
    Args:
        country: A string specifying the country
    Returns:
        Dictionary of currency regex patterns
    """
    patterns = {
        'sweden': {'kr': r'kr|kronor', 'sek': r'\b(?:sek)\b'},
        'france': {'€': r'€', 'eur': r'\b(?:eur|euros?)\b'},
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

def extract_numbers(text):
    """Extract valid numeric values, excluding 401k and numbers starting with 0."""
    pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:k)?\b'
    return pd.Series(re.findall(pattern, text)).dropna()[
        lambda x: ~x.str.startswith('0') & ~x.str.contains('401')
    ].map(
        lambda x: float(x[:-1].replace(',', '')) * 1000 if x.endswith('k') 
        else float(x.replace(',', ''))
    ).tolist()

def detect_salary_magnitude_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """Detect rows with salary magnitude mismatch."""
    mask = pd.notna(df['min_salary']) & pd.notna(df['max_salary'])
    magnitude_diff = (df[mask]['max_salary'].astype(int).astype(str).str.len() - 
                     df[mask]['min_salary'].astype(int).astype(str).str.len()).abs()
    
    return df[mask & (magnitude_diff >= 2)][['min_salary', 'max_salary', 'context_string']]
    
def extract_salary_info(text: str, currencies: dict) -> pd.Series:
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
                
                if numbers := [n for n in extract_numbers(context) 
                             if n != 0 and not any(re.search(pat.replace(r'\d+', r'\d*\.?\d*'), context) 
                                                 for pat in EXCLUDED_PATTERNS)]:
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
    # Preprocess text once
    lowered_text = df[text_column].str.lower()
    lowered_country = df['country'].str.lower()
    
    mask = lowered_country.eq(country.lower()) & \
           lowered_text.str.contains('salary|compensation|pay|wage', na=False)
    df_out = df[mask].copy()
    
    if df_out.empty:
        return df_out
        
    df_out[['min_salary', 'max_salary', 'currency', 'time_period', 'context_string']] = None
    df_out['salary_extraction_success'] = False
    
    currencies = get_currency_patterns(country)
    df_out.update(lowered_text[mask].apply(lambda x: extract_salary_info(x, currencies)))
    
    return df_out