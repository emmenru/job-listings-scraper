import re
from typing import List, Optional
import pandas as pd
import numpy as np

DEBUG = True

def get_currency_patterns(country: str) -> dict:
    """
    Allows us to use different currency patterns for different countries. 
    Args: 
        country: A string specifying the country. 
    Returns: 
        patterns: Dictionary of currency regex patterns for given country.
    """
    patterns = {
        'sweden': {'kr': r'kr|kronor', 'sek': r'\b(?:sek)\b'},
        'france': {'€': r'€', 'eur': r'\b(?:eur|euros?)\b'},
        'usa': {'$': r'\$', 'usd': r'\b(?:usd|dollars?)\b'},
        'us': {'$': r'\$', 'usd': r'\b(?:usd|dollars?)\b'}
    }
    return patterns.get(country.lower(), {})

def extract_time_unit(text: str) -> str:
    """
    Function that uses regex patterns to identify the time unit associated with the salary mentioned in the text.
    Args: 
        text: String to extract time unit from. Default for US: 'per year'
    Returns: 
        The identified time unit as a string. 
    """
    if re.search(r'\b(?:per\s+hour|hourly|/hour|/hr|/h)\b', text, re.I):
        return 'per hour'
    if re.search(r'\b(?:per\s+month|monthly|/month|/mo)\b', text, re.I):
        return 'per month'
    return 'per year'

def extract_numbers(text: str) -> List[float]:
    """
    Extracts numbers that might be salary figures, using regex patters. 
    Also filters out numbers less than 100 (remove this). 
    Args: 
        A text string that supposedly contains salary figures. 
    Returns: 
        Should extract a list of floats.
    """
    pattern = r'\b\d+(?:,\d+)?(?:\.\d+)?\b(?![a-zA-Z])'  # Matches numbers like 144,400.00 
    numbers = re.findall(pattern, text)  # Applies the regexp and extracts all matching numbers
    clean_numbers = pd.to_numeric(pd.Series(numbers).str.replace(',', ''))
    return clean_numbers

# Function to expand context if it starts or ends with a number (including decimals)
def expand_context_for_numbers(text, start, end):
    while start > 0 and re.match(r'[\d,\.]', text[start-1]):
        start -= 1
    while end < len(text) - 1 and re.match(r'[\d,\.]', text[end+1]):
        end += 1
    return start, end


def process_job_descriptions(df: pd.DataFrame, 
                           country: str, 
                           text_column: str = 'normalized_text') -> pd.DataFrame:
    """
    Extracts salary information from job descriptions.

    Args: 
        df: Our dataframe containing extracted data from Indeed. 
        country: String defining the country in question. 
        text_column: The column name that we will use to extract text.

    Returns: 
        DataFrame with extracted salary information.
    """  
    df_out = df[df['country'].str.lower() == country.lower()].copy()  # Filter on country 
    df_out[['min_salary', 'max_salary', 'currency', 'time_period', 'context_string']] = None  # Create new columns 
    df_out['salary_extraction_success'] = False

    # Terms to check for exclusion (e.g., ids and health care benefits)
    excluded_patterns = [
        r'\d+ billion',
        r'id \d+',
        r'us-\d+',
        r'\d+ pay detail',
        r'child low \d+', 
        r'retirement plan like \d+ dollar-for-dollar', 
        r'\d+ per-capita healthcare',
        r' leave \d+']

    currencies = get_currency_patterns(country)

    for idx, row in df_out.iterrows():
        try:
            text = str(row[text_column]).lower()  # Convert text to lowercase

            # Skip rows without salary context words ("salary", "compensation", etc.)
            if not any(word in text for word in ['salary', 'compensation', 'pay', 'wage']):
                continue

            for currency_symbol, pattern in currencies.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)  # Search for currency patterns
                for match in matches:
                    # Extract context window around the currency, expanding if it starts/ends with a number
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 40)
                    start, end = expand_context_for_numbers(text, start, end)

                    context = text[start:end]

                    if DEBUG:
                        print(f"\nRow {idx}: Found {currency_symbol}")
                        print(f"Context: '{context}'")

                    # Extract numbers from the expanded context
                    numbers = extract_numbers(context)
                    # Skip numbers that have value 0, starts with 0, or includes exclusion terms defined above
                    filtered_numbers = [num for num in numbers if num != 0 and 
                                        not any(re.search(pattern, context.lower()) for pattern in excluded_patterns) and
                                        not str(num).startswith('0')]
                    
                    if len(filtered_numbers) >= 1:  # If at least one valid number is found and values not zero
                        # Remove numbers if it seems this is not a salary number 
                        filtered_numbers = sorted(filtered_numbers)
                        if DEBUG:
                            print(f"Filtered numbers: {filtered_numbers}")
                        df_out.at[idx, 'min_salary'] = filtered_numbers[0]
                        df_out.at[idx, 'max_salary'] = filtered_numbers[-1]
                        df_out.at[idx, 'currency'] = currency_symbol
                        df_out.at[idx, 'time_period'] = extract_time_unit(context)
                        df_out.at[idx, 'salary_extraction_success'] = True
                        df_out.at[idx, 'context_string'] = context
                        if DEBUG:
                            print(f"Min value: {filtered_numbers[0]}, Max value: {filtered_numbers[-1]}")
                        break  # Stop processing after finding a valid salary context

        except Exception as e:
            if DEBUG:
                print(f"Error processing row {idx}: {str(e)}")
    return df_out