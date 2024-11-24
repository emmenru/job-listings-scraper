import re
import numpy as np
import pandas as pd
import string
from langdetect import detect, LangDetectException
import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk import download
from collections import Counter

import utils.dictionaries as dicts

# Download stopwords once 
downloaded_stopwords = {}
def download_stopwords(language):
  if language not in downloaded_stopwords:
    downloaded_stopwords[language] = set(stopwords.words(language))

def tokenize_and_filter(text, stop_words):
    # Tokenization: split text into words and remove stopwords
    tokens = text.split()
    return [word for word in tokens if word not in stop_words]

def preprocess_text(text):
    # Remove punctuation and make lowercase
    return re.sub(r'[^\w\s]', '', text.lower())

# Function to detect language 
def detect_language(text):
  try:
    return detect(text)
  except LangdetectException as e:
    # Handle specific language detection exceptions here
    return 'Unknown'

# Function to normalize text based on language
def normalize_text(text, language_code, language_map):
  # Map language codes to language names using language_map from dicts.py
  language = language_map.get(language_code, "Unknown")  # Default to "Unknown"

  # Download stopwords once per language (if not already downloaded)
  download_stopwords(language)

  # Lowercase
  text = text.lower()

  # Remove stop words
  stop_words = downloaded_stopwords[language]
  words = [word for word in text.split() if word not in stop_words]

  # Remove punctuation
  words = [word.strip(string.punctuation) for word in words]

  # Choose either stemming or lemmatization
  #stemmer = nltk.PorterStemmer()  # Use stemming (uncomment lemmatizer for lemmatization)
  #words = [stemmer.stem(word) for word in words]
  lemmatizer = nltk.WordNetLemmatizer()
  words = [lemmatizer.lemmatize(word) for word in words]

  # Join words back into a string
  normalized_text = ' '.join(words)
  return normalized_text

def normalize_group(group):
    print(f'Normalizing text for language group: {group.name}')
    group['job_description_norm'] = group['job_description'].apply(lambda x: normalize_text(x, group.name, dicts.language_map))
    return group

def extract_keywords(df, country, language):
    """
    Extracts and returns the most common keywords from job descriptions in a specified country and language.
    Args:
        df: The DataFrame containing job descriptions and other relevant columns.
        country: The country to filter the data by.
        language: The language of the job descriptions.
    Returns:
        A tuple containing:
            1. A list of the top 10 most common keywords.
            2. A list of all extracted tokens.
    """
    # Use the normalized job description text
    job_description_column = 'job_description_norm'
    
    # Create language-specific stopwords mapping
    language_stopwords = {
        'french': lambda: stopwords.words('english') + stopwords.words('french'),
        'italian': lambda: stopwords.words('english') + stopwords.words('italian'),
        'swedish': lambda: stopwords.words('english') + stopwords.words('swedish'),
        'english': lambda: stopwords.words('english')
    }
    
    # Get stopwords or raise error for unsupported language
    try:
        stop_words = set(language_stopwords[language]())
    except KeyError:
        raise ValueError(f"Unsupported language: {language}")
    
    # Filter and process text
    df_country = (df[df['country'] == country]
                 .assign(
                     cleaned_description=lambda x: x[job_description_column].apply(preprocess_text),
                     tokens=lambda x: x['cleaned_description'].apply(
                         lambda text: tokenize_and_filter(text, stop_words)
                     )
                 ))
    
    # Flatten tokens 
    all_tokens = df_country['tokens'].explode().tolist()
    
    # Get word counts and top keywords
    word_counts = Counter(all_tokens)
    common_keywords = word_counts.most_common(10)
    
    return common_keywords, all_tokens
    
def count_keywords(df, country, software_keywords, job_description_column):
    """
    Counts the presence (binary) of keywords in job descriptions for a specific country and categorizes them.
    Args:
        df: The DataFrame containing job descriptions and search keywords.
        country: The country to filter the data by.
        software_keywords: A dictionary mapping categories to lists of keywords.
    Returns:
        A DataFrame with columns for category, keyword, count, associated search keyword, and country.
    """
    # Use the normalized job description text
    #job_description_column = 'job_description_norm'
    
    # Filter by country and convert to lowercase once
    filtered_df = df[df['country'] == country].copy()
    filtered_df[job_description_column] = filtered_df[job_description_column].str.lower()
    
    # Create keyword DataFrame
    keyword_df = pd.DataFrame([
        (category, keyword)
        for category, keywords in software_keywords.items()
        for keyword in keywords
    ], columns=['Category', 'Keyword'])
    
    # Create cross join between filtered_df and keyword_df
    result = (filtered_df[[job_description_column, 'search_keyword']]
             .assign(key=1)
             .merge(keyword_df.assign(key=1), on='key')
             .drop('key', axis=1))
    
    # Binary count (1 if keyword present, 0 if not)
    result['Count'] = result.apply(
        lambda row: 1 if row['Keyword'] in row[job_description_column] else 0, 
        axis=1
    )
    
    # Filter non-zero counts and add country
    result = (result[result['Count'] > 0]
             .assign(Country=country)
             [['Category', 'Keyword', 'Count', 'search_keyword', 'Country']]
             .rename(columns={'search_keyword': 'Search Keyword'}))
    
    # Group and sum counts with observed parameter
    result = result.groupby(
        ['Category', 'Keyword', 'Search Keyword', 'Country'],
        as_index=False,
        observed=True  
    ).sum()
    
    return result


def extract_single_stage(text, pattern, language, context_patterns):
    """
    Extracts text around a specific interview stage pattern from job description text.
    
    Args:
        text: The job description text to search in
        pattern: Regex pattern for the interview stage
        language: Language code (e.g., 'en', 'fr', 'it', 'sv')
        context_patterns: Dictionary of context patterns by language
    
    Returns:
        Extracted text around the pattern or None if not found
    """
    context_pattern = context_patterns.get(language, context_patterns['english'])
    context_match = re.search(context_pattern, text, re.IGNORECASE)
    
    if context_match:
        text_after_context = text[context_match.end():]
        stage_match = re.search(pattern, text_after_context, re.IGNORECASE)
        
        if stage_match:
            start = max(0, stage_match.start() - 20)
            end = min(len(text_after_context), stage_match.end() + 100)
            return text_after_context[start:end].strip()
    return None


def extract_interview_details(df, stages, context_patterns, column, language_column='language'):
    """
    Extracts detailed information about interview stages from job descriptions.
    
    Args:
        df: DataFrame with job_description, job_id, job_title, and job_link columns
        stages: Dictionary with defined patterns for each interview stage
        context_patterns: Dictionary of context patterns by language
        column: The column containing job description text
        language_column: Column specifying the language of the job description
    
    Returns:
        Tuple of two DataFrames:
        1. Detailed text for each interview stage
        2. Boolean indicators for presence of each stage
    """
    base_df = df[['job_id', 'search_keyword', 'job_link', language_column]].copy()
    
    for stage, pattern in stages.items():
        base_df[f'{stage}_text'] = df.apply(
            lambda row: extract_single_stage(row[column], pattern, row[language_column], context_patterns), axis=1
        )
        base_df[stage] = base_df[f'{stage}_text'].notna()
    
    text_columns = ['job_id', 'search_keyword', 'job_link'] + [f'{s}_text' for s in stages]
    flag_columns = ['job_id', 'search_keyword', 'job_link'] + list(stages.keys())
    
    return base_df[text_columns], base_df[flag_columns]

    
'''
def extract_single_stage(text, pattern):
    """
    Extracts text around a specific interview stage pattern from job description text.
    
    Args:
        text: The job description text to search in
        pattern: Regex pattern for the interview stage
    
    Returns:
        Extracted text around the pattern or None if not found
    """
    # This should be based on language for respective country 
    context_pattern = r'recruitment process|interview process'
    context_match = re.search(context_pattern, text, re.IGNORECASE)
    
    if context_match:
        text_after_context = text[context_match.end():]
        stage_match = re.search(pattern, text_after_context, re.IGNORECASE)
        
        if stage_match:
            start = max(0, stage_match.start() - 20)
            end = min(len(text_after_context), stage_match.end() + 100)
            return text_after_context[start:end].strip()
    return None

def extract_interview_details(df, stages, context_patterns, column):
    """
    Extracts detailed information about interview stages from job descriptions.
    
    Args:
        df: DataFrame with job_description, job_id, job_title, and job_link columns
        stages: Dictionary with defined patterns for each interview stage
    
    Returns:
        Tuple of two DataFrames: 
        1. Detailed text for each interview stage
        2. Boolean indicators for presence of each stage
    """
    base_df = df[['job_id', 'search_keyword', 'job_link']].copy()
    
    for stage, pattern in stages.items():
        base_df[f'{stage}_text'] = df[column].apply(
            lambda x: extract_single_stage(x, pattern)
        )
        base_df[stage] = base_df[f'{stage}_text'].notna()
    
    text_columns = ['job_id', 'search_keyword', 'job_link'] + [f'{s}_text' for s in stages]
    flag_columns = ['job_id', 'search_keyword', 'job_link'] + list(stages.keys())
    
    return base_df[text_columns], base_df[flag_columns]
'''