import re
import pandas as pd
import numpy as np

DEBUG = False

PATTERNS = {
    'salary_terms': {
        'usa': "salary|compensation|pay|wage",
        'france': "salaire|rémunération|revenu|taux horaire|conditions salariales",
        'sweden': "lön|betalning|salary|compensation|pay|wage",
        'italy': "stipendio|retribuzione|salario|compenso|paga|ral|rimborso|salary|compensation|pay|wage"
    },
    'numbers': {
        'usa': r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:k)?\b',
        'sweden': r'\b\d+(?:\s?\d{3})*(?:,\d+)?\b',
        'france': r'\b\d+(?:\s?\d{3})*(?:[,.]\d+)?\b',    
        'italy': r'\b\d+(?:[,.]\d+)*(?:k)?\b|\b\d+(?:[-–]\d+)?k?\b'
    },
    'time': {
        'french': {
            'per hour': "par\s+heure|horaire|/heure|/h|heure",
            'per day': "par\s+jour|journalier|/jour|/j|jour",
            'per week': "par\s+semaine|hebdomadaire|/semaine|semaine",
            'per month': "par\s+mois|mensuel|/mois|mois",
            'per year': "par\s+an|annuel|/an|annee|an"
        },
        'english': {
            'per hour': "per\s+hour|hourly|/hour|/hr|/h",
            'per week': "per\s+week|weekly|/week|/wk|/w",
            'per month': "per\s+month|monthly|/month|/mo",
            'per year': "per\s+year|yearly|annual|/year|/yr"
        },
        'italian': {
            'per hour': "all\'ora|ora|orario|/ora",
            'per day': "al\s+giorno|giornaliero|/giorno",
            'per week': "alla\s+settimana|settimanale|/settimana",
            'per month': "al\s+mese|mensile|/mese",
            'per year': "all\'anno|annuale|/anno|ral"
        }
    },
    'currency': {
        'sweden': {'kr': r'kr|kronor', 'sek': r'\b(?:sek)\b'},
        'france': {'€': r'€', 'eur': r'\b(?:eur|euros?)\b'},
        'italy': {'€': r'€', 'eur': r'\b(?:eur|euros?)\b'},
        'usa': {'$': r'\$', 'usd': r'\b(?:usd|dollars?)\b'}
    }
}

SALARY_LIMITS = {
    'usa': {'hourly': (1, 1000), 'other': (15000, 1000000)},
    'france': {'hourly': (36, 500), 'weekly': (100, 7000), 'other': (500, 100000)},
    'sweden': {'hourly': (250, 10000), 'other': (6000, 1000000)},
    'italy': {'hourly': (1, 500), 'other': (200, 200000)}
}

def parse_number(x: str, country: str) -> float:
    """Parse number strings with country-specific formats."""
    # France/Italy: switch commas to decimals
    # Others: remove commas
    has_k = 'k' in x.lower()
    x = x.lower().strip().replace('k', '').replace(' ', '').replace('\u00a0', '')
    if country in ['france', 'italy']:
        x = x.replace('.', '').replace(',', '.')
    else:
        x = x.replace(',', '')
    return float(x) * (1000 if has_k else 1)

def is_likely_year(number: float, context: str) -> bool:
    """Check if a number is likely to be a year."""
    if number.is_integer() and 2010 <= number <= 2030:
        number_str = str(int(number))
        year_patterns = [rf'\b{number_str}\b', rf'en\s+{number_str}\b', rf'depuis\s+{number_str}\b', rf'à partir de\s+{number_str}\b']
        return any(re.search(pattern, context.lower()) for pattern in year_patterns)
    return False

'''
def expand_context_for_numbers(text: str, start: int, end: int) -> tuple[int, int]:
    """Expand context to include complete numbers at boundaries."""
    while start > 0 and re.match(r'[\d,\.]', text[start-1]):
        start -= 1
    while end < len(text) - 1 and re.match(r'[\d,\.]', text[end+1]):
        end += 1
    return start, end
'''

def expand_context_for_numbers(text: str, start: int, end: int) -> tuple[int, int]:
    """Expand context if numbers at boundaries don't have proper delimiters."""
    # Check start boundary - expand if number doesn't have starting delimiter
    if start > 0 and re.match(r'\d', text[start]) and not re.match(r'[^\d,\.]', text[start-1]):
        while start > 0 and re.match(r'[\d,\.]', text[start-1]):
            start -= 1
    # Check end boundary - expand if number doesn't have ending delimiter
    if end < len(text)-1 and re.match(r'\d', text[end]) and not re.match(r'[^\d,\.]', text[end+1]):
        while end < len(text)-1 and re.match(r'[\d,\.]', text[end+1]):
            end += 1
    return start, end

def extract_time_unit(text: str, language: str = 'english', country: str = 'usa') -> str:
   """Extract time unit closest to salary numbers."""
   text = text.lower()
   patterns = PATTERNS['time'].get(language, PATTERNS['time']['english'])
   default = 'per month' if country in ['sweden', 'france', 'italy'] else 'per year'
   if country == 'france' and re.search(r'\b[1-9]\d{4,}\b', text):
       return 'per year'
   num_pos = [m.start() for m in re.finditer(PATTERNS['numbers'][country], text)]
   if not num_pos:
       return default
   matches = [(re.search(pattern, text, re.I).start(), unit) 
              for unit, pattern in patterns.items()
              if re.search(pattern, text, re.I)]
   return min(matches, key=lambda x: min(abs(x[0] - p) for p in num_pos))[1] if matches else default
    
def extract_salary_info(text: str, country: str, language: str = 'english') -> pd.Series:
    """Extract salary information from respective row."""
    time_to_limit = {'per hour': 'hourly','per week': 'weekly'}
    # Format for output series 
    default_result = pd.Series({key: None for key in ['min_salary', 'max_salary', 'currency', 'time_period', 'context_string', 'initial_numbers']})
    default_result['salary_extraction_success'] = False
    if not isinstance(text, str):
        return default_result 
    text = text.lower()
    try: 
        for currency_symbol, pattern in PATTERNS['currency'][country].items():
            for match in re.finditer(pattern, text):
                # Get string context around the match 
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 40)
                # If number is cut off at start or ending, expand the captured string
                start, end = expand_context_for_numbers(text, start, end)
                context = text[start:end]
                if not re.search(PATTERNS['salary_terms'][country], context):
                    continue
                # Extract numbers from context string based on patterns for respective country 
                numbers = pd.Series(re.findall(PATTERNS['numbers'][country], context))
                if numbers.empty:
                    continue
                # All unfiltered numbers 
                initial_numbers = numbers.apply(lambda x: parse_number(x, country)).tolist() 
                if DEBUG: 
                    print(f'Detected numbers: {initial_numbers}')
                # Make sure zeroes are removed 
                numbers = pd.Series([n for n in initial_numbers if n != 0])
                # Remove numbers that likely are years (e.g. for standard salaries for certain years, e.g. 2024)
                numbers = numbers[~numbers.apply(lambda x: is_likely_year(x, context))] 
                # Get the time period for the salary (e.g. per hour, per year, etc.)
                time_period = extract_time_unit(context, language, country)
                # Set salary limits that filter out unreasonable numbers for respective country
                limits = SALARY_LIMITS[country][time_to_limit.get(time_period, 'other')]
                numbers = numbers[(numbers >= limits[0]) & (numbers <= limits[1])]
                if DEBUG: 
                    print(f'Filtered numbers (after year and limit checks): {numbers.tolist()}')
                if not numbers.empty:
                    return pd.Series({'min_salary': numbers.min(),
                        'max_salary': numbers.max(),
                        'currency': currency_symbol,
                        'time_period': time_period,
                        'context_string': context,
                        'initial_numbers': initial_numbers,
                        'salary_extraction_success': True
                    })
    except Exception as e:
        print(f'Error: {e}')
        return default_result
    return default_result

def process_job_descriptions(df: pd.DataFrame, country: str, text_column: str = 'normalized_text') -> pd.DataFrame:
    """Filters dataframe for relevant country and salary terms. Creates copy of filtered df. Applies extract_salary_info to each row."""
    country = country.lower()
    if country not in PATTERNS['salary_terms']:
        raise ValueError(f'Salary terms not found for country: {country}')
    # Boolean mask for filtering df for resp. country, that also contains salary-related terms specified in PATTERNS
    mask = (df['country'].str.lower() == country) & df[text_column].str.lower().str.contains(PATTERNS['salary_terms'][country], na=False)
    df_out = df[mask].copy()
    # Don't process if no match is found
    if df_out.empty:
        return df_out
    # Apply extract_salary_info() to all rows in the dataset and save results as df_out
    result_columns = ['min_salary', 'max_salary', 'currency', 'time_period', 'context_string', 'initial_numbers', 'salary_extraction_success']
    df_out[result_columns] = df_out.apply(lambda row: extract_salary_info(row[text_column], country, row['language']),axis=1)
    return df_out

def detect_salary_magnitude_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """Detect salary magnitude mismatches, i.e. when min value doesnt match magnitude of max value by 2 digit size (for debugging purposes)."""
    mask = df[['min_salary', 'max_salary']].notna().all(axis=1) # Instances where there are both min and max values 
    magnitude_diff = np.abs(df[mask]['max_salary'].astype(int).astype(str).str.len() - df[mask]['min_salary'].astype(int).astype(str).str.len())
    return df[mask & (magnitude_diff >= 2)][['min_salary', 'max_salary', 'context_string']]