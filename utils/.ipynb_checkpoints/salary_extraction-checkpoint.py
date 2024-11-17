import re
from typing import List, Tuple
import pandas as pd

DEBUG = True  # Set to True to see all debug prints

def get_currency_patterns(country: str) -> dict:
    """
    Get currency patterns specific to a country.
    """
    patterns = {
        'sweden': {
            'kr': r'kr|kronor',
            'sek': r'\b(?:sek)\b'
        },
        'france': {
            '€': r'€',
            'eur': r'\b(?:eur|euros?)\b'
        },
        'usa': {
            '$': r'\$',
            'usd': r'\b(?:usd|dollars?)\b'
        },
        'us': {
            '$': r'\$',
            'usd': r'\b(?:usd|dollars?)\b'
        }
    }
    return patterns.get(country.lower(), {})

def is_salary_context(text: str) -> bool:
    """
    Check if the text contains salary-related terms.
    """
    salary_patterns = [
        r'salary',
        r'(?:base\s+(?:pay|salary)|total\s+compensation|compensation(?:\s+range)?)',
        r'(?:salary|pay|hiring|current)\s+range',
        r'range\s+(?:role|position)',
        r'role\s+(?:targeted|usd)',
        r'40\s+hour\s+pay',
        r'rate.*?per\s+hour',
        r'(?:usd|salary)\s+per\s+year',
        r'(?:salary|benefit)s?\s+offer(?:ed)?',
        r'usd\s+(?:location|los\s+angeles|west|new\s+york)',
        r'min\s+usd',
        r'pay\s+detail',
        r'minimum\s+salary',
        r'full\s+time\s+(?:schedule|position)'
    ]
    
    combined_pattern = '|'.join(fr'\b{pattern}\b' for pattern in salary_patterns)
    return bool(re.search(combined_pattern, text.lower()))

def normalize_number(num_str: str) -> float:
    """Convert number string to float for proper comparison."""
    # Remove any currency symbols and commas
    clean_str = num_str.replace('$', '').replace(',', '')
    try:
        return float(clean_str)
    except ValueError:
        return 0

def extract_numbers_from_context(context: str) -> List[str]:
    """
    Extract all numbers from the context string.
    Returns original strings but sorts by numeric value.
    """
    number_pattern = r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b|\b\d+k?\b'
    numbers = re.findall(number_pattern, context)
    return numbers

def extract_time_unit(context: str) -> str:
    """
    Extract time unit from context.
    Returns 'per year', 'per month', 'per hour', or None
    """
    time_patterns = {
        'per year': [
            r'per\s+year',
            r'annual',
            r'annually',
            r'/\s*year',
            r'/\s*yr',
            r'yearly'
        ],
        'per month': [
            r'per\s+month',
            r'monthly',
            r'/\s*month',
            r'/\s*mo'
        ],
        'per hour': [
            r'per\s+hour',
            r'hourly',
            r'/\s*hour',
            r'/\s*hr',
            r'/\s*h'
        ]
    }
    
    context = context.lower()
    
    for time_unit, patterns in time_patterns.items():
        combined_pattern = '|'.join(patterns)
        if re.search(combined_pattern, context):
            return time_unit
            
    return None

def process_job_descriptions(df: pd.DataFrame, 
                           country: str,
                           text_column: str = 'job_description',
                           country_column: str = 'country') -> pd.DataFrame:
    """
    Find and print text containing currency indicators.
    If salary terms are present, extract min and max numbers and time unit.
    Defaults to 'per year' if no time unit found.
    """
    df_country = df[df[country_column].str.lower() == country.lower()].copy()
    
    if len(df_country) == 0:
        if DEBUG: print(f"No records found for country: {country}")
        return df_country
    
    df_country['min_salary'] = None
    df_country['max_salary'] = None
    df_country['currency'] = None
    df_country['time_period'] = None
    df_country['salary_extraction_success'] = False
    
    if DEBUG: print(f"\nProcessing rows for {country}:")
    if DEBUG: print("-" * 100)
    
    currencies = get_currency_patterns(country)
    
    for idx, row in df_country.iterrows():
        try:
            text = str(row[text_column]).lower()
            all_numbers = []
            found_currency = None
            found_time_unit = None
            valid_contexts = []  # Store all valid contexts
            
            for currency_symbol, pattern in currencies.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 40)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end]
                    
                    if is_salary_context(context):
                        if DEBUG: print(f"\nRow {idx}: Found {currency_symbol}")
                        if DEBUG: print(f"Context: '{context}'")
                        
                        numbers = extract_numbers_from_context(context)
                        if numbers:
                            all_numbers.extend(numbers)
                            found_currency = currency_symbol
                            valid_contexts.append(context)
                            if DEBUG: print(f"Numbers found in this context: {numbers}")
            
            # After collecting all numbers and contexts, find global min and max
            if all_numbers:
                numeric_values = [(n, normalize_number(n)) for n in all_numbers]
                sorted_values = sorted(numeric_values, key=lambda x: x[1])
                
                min_value = sorted_values[0][0]
                max_value = sorted_values[-1][0]
                
                # Look for time unit in all valid contexts
                for context in valid_contexts:
                    time_unit = extract_time_unit(context)
                    if time_unit:
                        found_time_unit = time_unit
                        break
                
                # Default to 'per year' if no time unit found
                if found_time_unit is None:
                    found_time_unit = 'per year'
                
                if DEBUG: print(f"All numbers found: {all_numbers}")
                if DEBUG: print(f"Global min value: {min_value}")
                if DEBUG: print(f"Global max value: {max_value}")
                if DEBUG: print(f"Time unit found: {found_time_unit}")
                
                # Update DataFrame with found values
                df_country.at[idx, 'min_salary'] = min_value
                df_country.at[idx, 'max_salary'] = max_value
                df_country.at[idx, 'currency'] = found_currency
                df_country.at[idx, 'time_period'] = found_time_unit
                df_country.at[idx, 'salary_extraction_success'] = True
                    
            if DEBUG: print("-" * 100)
            
        except Exception as e:
            if DEBUG: print(f"Error processing row {idx}: {str(e)}")
            continue
    
    # Print summary
    successful_rows = df_country['salary_extraction_success'].sum()
    total_rows = len(df_country)
    print(f"\nProcessing Summary for {country}:")
    print(f"Total rows processed: {total_rows}")
    print(f"Successful extractions: {successful_rows}")
    print(f"Success rate: {(successful_rows/total_rows)*100:.2f}%")
    
    return df_country