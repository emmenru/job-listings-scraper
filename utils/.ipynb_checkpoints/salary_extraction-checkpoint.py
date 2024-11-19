import re
from typing import List, Optional
import pandas as pd
import numpy as np

DEBUG = False

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
    pattern = r'\b[1-9]\d*(?:,\d+)?(?:\.\d+)?(?:k)?\b'
    numbers = re.findall(pattern, text)
    
    cleaned = []
    for num in numbers:
        if num.lower().endswith('k') and not num.startswith('401'): # This corresponds to US 401k plans
            if DEBUG: 
                print(f'Found a K!, {num}')
            num = float(num[:-1].replace(',', '')) * 1000
        else:
            num = float(num.replace(',', ''))
        cleaned.append(num)
    
    return cleaned
    
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
   """  
   df_out = df[df['country'].str.lower() == country.lower()].copy()
   df_out[['min_salary', 'max_salary', 'currency', 'time_period', 'context_string']] = None
   df_out['salary_extraction_success'] = False
   
   excluded_patterns = [
       r'\d+\.?\d*\s*billion',
       r'id \d+',
       r'us-\d+',
       r'\d+ pay detail',
       r'child low \d+', 
       r'retirement plan like \d+ dollar-for-dollar', 
       r'\d+ per-capita healthcare',
       r' leave \d+']
   
   currencies = get_currency_patterns(country)
   salary_keywords = ['salary', 'compensation', 'pay', 'wage']
   
   for idx, row in df_out.iterrows():
       try:
           text = str(row[text_column]).lower()
           
           # Single keyword check per row
           matched_keywords = [word for word in salary_keywords if word in text]
           if not matched_keywords:
               continue # Not likely to be a salary number, exit
               
           if DEBUG:
               print(f"Row {idx} - Found keywords: {matched_keywords}")
           
           found_salary = False
           for currency_symbol, pattern in currencies.items():
               if found_salary:
                   break
                   
               matches = re.finditer(pattern, text, re.IGNORECASE)
               for match in matches:
                   start = max(0, match.start() - 50)
                   end = min(len(text), match.end() + 40)
                   start, end = expand_context_for_numbers(text, start, end)
                   context = text[start:end]
                   
                   if DEBUG:
                       print(f"Row {idx}: Found {currency_symbol}")
                       print(f"Context: '{context}'")
                       
                   numbers = extract_numbers(context)
                   numbers = extract_numbers(context)
                   filtered_numbers = [num for num in numbers if num != 0 and 
                                       not any(re.search(pat.replace(r'\d+', r'\d*\.?\d*'), context) 
                                               for pat in excluded_patterns) and not str(num).startswith('0')]
                                     
                   if len(filtered_numbers) >= 1:
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
                       found_salary = True
                       break
                       
       except Exception as e:
           if DEBUG:
               print(f"Error processing row {idx}: {str(e)}")
               
   return df_out