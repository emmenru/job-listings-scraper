import re
from typing import List, Optional
import pandas as pd

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
    pattern = r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b'  # Matches numbers like 144,400.00 . What if monthly salaries, i.e. 10,000?
    numbers = re.findall(pattern, text) # Applies the regexp and extracts all matching numbers
    # do this later
    numbers_as_floats = [float(num.replace(',', '')) for num in numbers]
    return numbers_as_floats 

def process_job_descriptions(df: pd.DataFrame, 
                               country: str, 
                               text_column: str = 'normalized_text') -> pd.DataFrame:
    """
    Extracts salary information from job descriptions.

    Args: 
        df: Our dataframe containing extracted data from Indeed. 
        country: String defining the country in question. 
        text_colum: The column name that we will use to extract text.

    Returns: 
        DataFrame with extracted salary information.
    """  
    df_out = df[df['country'].str.lower() == country.lower()].copy() # Filter on country 
    df_out[['min_salary', 'max_salary', 'currency', 'time_period']] = None  # Create new columns 
    df_out['salary_extraction_success'] = False

    currencies = get_currency_patterns(country)

    for idx, row in df_out.iterrows():
        try:
            text = str(row[text_column]).lower() # Convert text into string and make sure it is lowercase 
            
            # Look for salary context
            if not any(word in text for word in ['salary', 'compensation', 'pay', 'wage']):
                continue # Assumes this row doesn't contain relevant salary information
            
            # If salary context is found, iterate through each currency symbol and its corresponding pattern   
            for currency_symbol, pattern in currencies.items():
                matches = re.finditer(pattern, text, re.IGNORECASE) # search for all occurrences of the pattern in the text
                for match in matches:
                    # Extract context window around the currency
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 40)
                    context = text[start:end]

                    # Filter out contexts indicating work week duration using regex
                    if re.search(r'\b\d+\s*/\s*\d+\s*standard\s*work\s*schedule\b', context, re.IGNORECASE):
                        continue

                    if DEBUG: print(f"\nRow {idx}: Found {currency_symbol}")
                    if DEBUG: print(f"Context: '{context}'")

                    numbers = extract_numbers(context)
                    if len(numbers) >= 1: # If at least one number is found, populate dataframe with results 
                        numbers = sorted(numbers)
                        if DEBUG: print(f"Numbers found: {numbers}")
                        df_out.at[idx, 'min_salary'] = numbers[0]
                        df_out.at[idx, 'max_salary'] = numbers[-1]
                        df_out.at[idx, 'currency'] = currency_symbol
                        df_out.at[idx, 'time_period'] = extract_time_unit(context)
                        df_out.at[idx, 'salary_extraction_success'] = True
                        break
        except Exception as e:
            if DEBUG: print(f"Error processing row {idx}: {str(e)}")
    return df_out