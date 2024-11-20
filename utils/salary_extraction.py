"""Functions for extracting salary information from job descriptions."""

import re
import pandas as pd
import numpy as np

# Constants
ENGLISH_TERMS = "salary|compensation|pay|wage"

SALARY_TERMS = {
    'usa': [ENGLISH_TERMS],
    'france': [f"salaire|rémunération|revenu|taux horaire|conditions salariales"],
    'sweden': [f"lön|betalning|{ENGLISH_TERMS}"],
    'italy': [ENGLISH_TERMS]
}

NUMBER_PATTERNS = {
    'usa': r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:k)?\b',
    'sweden': r'\b\d+(?:\s?\d{3})*(?:,\d+)?\b',
    'france': r'\b\d+(?:\s?\d{3})*(?:[,.]\d+)?\b',
    'italy': r'\b\d+(?:\.?\d{3})*(?:,\d+)?\b'
}

TIME_PATTERNS = {
    'french': {
        'per hour': r'\b(?:par\s+heure|horaire|/heure|/h|heure)\b',
        'per day': r'\b(?:par\s+jour|journalier|/jour|/j|jour)\b',
        'per week': r'\b(?:par\s+semaine|hebdomadaire|/semaine|semaine)\b',
        'per month': r'\b(?:par\s+mois|mensuel|/mois|mois)\b',
        'per year': r'\b(?:par\s+an|annuel|/an|annee|an)\b'
    },
    'english': {
        'per hour': r'\b(?:per\s+hour|hourly|/hour|/hr|/h)\b',
        'per week': r'\b(?:per\s+week|weekly|/week|/wk|/w)\b',
        'per month': r'\b(?:per\s+month|monthly|/month|/mo)\b',
        'per year': r'\b(?:per\s+year|yearly|annual|/year|/yr)\b'
    },
    'italian': {
        'per hour': r'\b(?:all\'ora|ora|orario|/ora)\b',
        'per day': r'\b(?:al\s+giorno|giornaliero|/giorno)\b',
        'per week': r'\b(?:alla\s+settimana|settimanale|/settimana)\b',
        'per month': r'\b(?:al\s+mese|mensile|/mese)\b',
        'per year': r'\b(?:all\'anno|annuale|/anno)\b'
    }
}

SALARY_LIMITS = {
    'usa': {'hourly': (1, 1000), 'other': (15000, 1000000)},
    'france': {'hourly': (36, 500), 'weekly': (100, 7000), 'other': (500, 100000)},
    'sweden': {'hourly': (250, 10000), 'other': (6000, 1000000)},
    'italy': {'hourly': (1, 500), 'other': (200, 100000)}
}

# Helper functions
def get_currency_patterns(country: str) -> dict:
    """Get currency patterns for different countries."""
    euro_pattern = {'€': r'€', 'eur': r'\b(?:eur|euros?)\b'}
    patterns = {
        'sweden': {'kr': r'kr|kronor', 'sek': r'\b(?:sek)\b'},
        'france': euro_pattern,
        'italy': euro_pattern,
        'usa': {'$': r'\$', 'usd': r'\b(?:usd|dollars?)\b'}
    }
    return patterns.get(country.lower(), {})

def parse_french_number(x: str) -> float:
    """Parse number in French or English format."""
    if ',' in x and len(x.split(',')[1]) == 3:
        return float(x.replace(',', ''))
    return float(x.replace(' ', '').replace('\u00a0', '').replace(',', '.'))

def is_likely_year(number: float, context: str) -> bool:
    """Check if a number is likely to be a year."""
    if number.is_integer() and 1900 <= number <= 2030:
        number_str = str(int(number))
        year_patterns = [
            rf'\b{number_str}\b',
            rf'en\s+{number_str}\b',
            rf'depuis\s+{number_str}\b',
            rf'à partir de\s+{number_str}\b'
        ]
        return any(re.search(pattern, context.lower()) for pattern in year_patterns)
    return False

def extract_time_unit(text: str, language: str = 'english', country: str = 'usa') -> str:
    """Extract payment time unit from text."""
    text = text.lower()
    country = country.lower()
    
    if country == 'france' and re.search(r'\b[1-9]\d{4,}\b', text):
        return 'per year'
        
    patterns = TIME_PATTERNS.get(language, TIME_PATTERNS['english'])
    
    for unit, pattern in patterns.items():
        if re.search(pattern, text, re.I):
            return unit
            
    return 'per month' if country in ['sweden', 'france', 'italy'] else 'per year'

def extract_numbers(text: str, country: str) -> list:
    """Extract and parse numbers from text."""
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
        parsed_numbers = numbers.apply(parse_french_number).tolist()
        return [n * 1000 if re.search(rf'{int(n)}\s*k', text, re.I) else n for n in parsed_numbers]
        
    else:  # italy
        return numbers.apply(lambda x: float(x.replace('.', '').replace(',', '.'))).tolist()

def expand_context_for_numbers(text: str, start: int, end: int) -> tuple[int, int]:
    """Expand context to include complete numbers at boundaries."""
    while start > 0 and re.match(r'[\d,\.]', text[start-1]):
        start -= 1
    while end < len(text) - 1 and re.match(r'[\d,\.]', text[end+1]):
        end += 1
    return start, end

# Main functions
def extract_salary_info(text: str, currencies: dict, country: str, language: str = 'english') -> pd.Series:
    """Extract salary information from text."""
    default_result = pd.Series({
        'min_salary': None, 'max_salary': None, 'currency': None,
        'time_period': None, 'context_string': None, 'initial_numbers': None,
        'salary_extraction_success': False
    })
    
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
                
                if not bool(re.search(SALARY_TERMS[country.lower()][0], context.lower())):
                    continue
                    
                initial_numbers = extract_numbers(context, country)
                initial_numbers = [n for n in initial_numbers if n != 0]
                time_period = extract_time_unit(context, language, country)
                
                limits = SALARY_LIMITS[country.lower()]
                min_limit, max_limit = (limits['hourly'] if time_period == 'per hour'
                                      else limits['weekly'] if time_period == 'per week'
                                      else limits['other'])
                
                numbers = [n for n in initial_numbers if not is_likely_year(n, context)]
                numbers = [n for n in numbers if min_limit <= n <= max_limit]
                
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

def process_job_descriptions(df: pd.DataFrame, country: str, 
                           text_column: str = 'normalized_text') -> pd.DataFrame:
    """Process job descriptions to extract salary information."""
    if country.lower() not in SALARY_TERMS:
        raise ValueError(f"Salary terms not found for country: {country}")
    
    # Filter relevant rows
    mask = (df['country'].str.lower() == country.lower()) & \
           df[text_column].str.lower().str.contains(SALARY_TERMS[country.lower()][0], na=False)
    df_out = df[mask].copy()
    
    if df_out.empty:
        return df_out
    
    # Initialize columns
    df_out[['min_salary', 'max_salary', 'currency', 'time_period', 'context_string']] = None
    df_out['salary_extraction_success'] = False
    
    # Extract salary information
    currencies = get_currency_patterns(country)
    df_out.update(df_out.apply(
        lambda row: extract_salary_info(row[text_column], currencies, country, row['language']),
        axis=1
    ))
    
    return df_out

def detect_salary_magnitude_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """Detect rows with salary magnitude mismatch."""
    mask = pd.notna(df['min_salary']) & pd.notna(df['max_salary'])
    magnitude_diff = (df[mask]['max_salary'].astype(int).astype(str).str.len() - 
                     df[mask]['min_salary'].astype(int).astype(str).str.len()).abs()
    
    return df[mask & (magnitude_diff >= 2)][['min_salary', 'max_salary', 'context_string']]