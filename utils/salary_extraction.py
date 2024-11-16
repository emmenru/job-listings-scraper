# Import required libraries
import spacy
import pandas as pd
import re
from typing import Tuple, Optional

def load_spacy_models():
    """Load spaCy models for different languages."""
    models = {
        'english': spacy.load('en_core_web_sm'),
        'french': spacy.load('fr_core_news_sm'),
        'italian': spacy.load('it_core_news_sm'),
        'swedish': spacy.load('sv_core_news_sm')
    }
    return models

def extract_currency_symbol(text: str) -> str:
    """Extract currency symbols or codes."""
    currency_patterns = {
        r'[\$€£]': lambda x: x,  # Common symbols
        r'\b(USD|EUR|GBP|SEK)\b': lambda x: {'USD': '$', 'EUR': '€', 'GBP': '£', 'SEK': 'kr'}[x]
    }
    
    for pattern, converter in currency_patterns.items():
        match = re.search(pattern, text)
        if match:
            return converter(match.group())
    return ''

def extract_time_period(text: str) -> str:
    """Extract time period for salary."""
    time_patterns = {
        'per hour': r'\b(per hour|hourly|/hour|/hr)\b',
        'per month': r'\b(per month|monthly|/month)\b',
        'per year': r'\b(per year|yearly|annual|/year|pa|p\.a\.)\b'
    }
    
    text = text.lower()
    for period, pattern in time_patterns.items():
        if re.search(pattern, text):
            return period
    return 'per year'  # default to annual

def extract_salary_range(text: str, nlp) -> Tuple[Optional[float], Optional[float]]:
    """Extract minimum and maximum salary numbers using spaCy."""
    doc = nlp(text)
    numbers = []
    
    # Extract numbers from text
    for ent in doc.ents:
        if ent.label_ in ['MONEY', 'CARDINAL', 'NUMBER']:
            # Clean and convert number string to float
            num_str = re.sub(r'[^\d.]', '', ent.text)
            try:
                num = float(num_str)
                if 1000 <= num <= 1000000:  # Reasonable salary range
                    numbers.append(num)
            except ValueError:
                continue
    
    if not numbers:
        return None, None
    
    return min(numbers), max(numbers)

def process_job_descriptions(df: pd.DataFrame, 
                           text_column: str = 'job_description',
                           lang_column: str = 'language') -> pd.DataFrame:
    """Process job descriptions and extract salary information."""
    # Load spaCy models
    models = load_spacy_models()
    
    # Initialize new columns
    df['min_salary'] = None
    df['max_salary'] = None
    df['currency'] = ''
    df['time_period'] = ''
    
    for idx, row in df.iterrows():
        text = str(row[text_column])
        language = str(row[lang_column]).lower()  # Use existing language column
        
        # Get appropriate model
        nlp = models.get(language)
        if nlp is None:
            print(f"Warning: No model available for language: {language}")
            continue
            
        # Extract salary information
        min_salary, max_salary = extract_salary_range(text, nlp)
        currency = extract_currency_symbol(text)
        time_period = extract_time_period(text)
        
        # Update DataFrame
        df.at[idx, 'min_salary'] = min_salary
        df.at[idx, 'max_salary'] = max_salary
        df.at[idx, 'currency'] = currency
        df.at[idx, 'time_period'] = time_period
    
    return df