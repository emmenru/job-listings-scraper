import re
import string
from collections import Counter
from typing import Dict, List, Set, Tuple

import nltk
import pandas as pd
from langdetect import detect, LangDetectException
from nltk import download
from nltk.corpus import stopwords

from utils.dictionaries import (COUNTRIES_LANGUAGES, COUNTRY_CODE_MAP, 
                              CONTEXT_PATTERNS, INTERVIEW_STAGES, LANGUAGE_MAP)
import utils.dictionaries as dicts

downloaded_stopwords: Dict[str, Set[str]] = {}
PUNCT_REGEX = r'[^\w\s]'

STOPWORD_MAP = {
    'french': lambda: stopwords.words('english') + stopwords.words('french'),
    'italian': lambda: stopwords.words('english') + stopwords.words('italian'), 
    'swedish': lambda: stopwords.words('english') + stopwords.words('swedish'),
    'english': lambda: stopwords.words('english'),
}

swedish_stopwords = set(stopwords.words('swedish'))
french_stopwords = set(stopwords.words('french'))
italian_stopwords = set(stopwords.words('italian'))
english_stopwords = set(stopwords.words('english'))

COUNTRIES_STOPWORDS = {
    'SWE': [swedish_stopwords, 'swedish'],
    'FRA': [french_stopwords, 'french'],
    'ITA': [italian_stopwords, 'italian'],
    'USA': [english_stopwords, 'english']
}

def download_stopwords(language: str) -> None:
    '''Download NLTK stopwords for given language if not already downloaded.'''
    if language not in downloaded_stopwords:
        download('punkt', quiet=True)
        download('wordnet', quiet=True)
        downloaded_stopwords[language] = set(stopwords.words(language))

def tokenize_and_filter(text: str, stop_words: Set[str]) -> List[str]:
    '''Tokenize text and remove stopwords.'''
    tokens = text.split()
    return [token for token in tokens if token not in stop_words]

def preprocess_text(text: str) -> str:
    '''Remove punctuation and convert to lowercase.'''
    return re.sub(PUNCT_REGEX, '', text.lower())

def detect_language(text: str) -> str:
    '''Detect text language using langdetect.'''
    try:
        return detect(text)
    except LangDetectException:
        return 'Unknown'

def normalize_text(text: str, language_code: str, language_map: Dict[str, str]) -> str:
    '''Normalize text by lowercasing, lemmatizing and removing stopwords.'''
    language = language_map.get(language_code, 'Unknown')
    download_stopwords(language)
    
    text = text.lower()
    words = tokenize_and_filter(text, downloaded_stopwords.get(language, set()))
    words = [word.strip(string.punctuation) for word in words]
    
    lemmatizer = nltk.WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    
    return ' '.join(words)

def normalize_group(group: pd.DataFrame) -> pd.DataFrame:
    '''Normalize job descriptions for a language group.'''
    print(f'Normalizing text for language group: {group.name}')
    group['job_description_norm'] = group['job_description'].apply(
        lambda x: normalize_text(x, group.name, LANGUAGE_MAP))
    return group

def extract_keywords(df: pd.DataFrame, country_name: str) -> Tuple[List[Tuple[str, int]], List[str]]:
    '''Extract most common keywords from job descriptions.'''
    country_code = COUNTRY_CODE_MAP[country_name]
    language = dicts.COUNTRIES_LANGUAGES[country_code][1]
    stop_words = set(stopwords.words(language))
    
    print(f'Rows for {country_name}: {len(df[df["country"] == country_name])}')
    
    df_filtered = (df[df['country'] == country_name]
                  .assign(cleaned_description=lambda x: x['job_description_norm'].apply(preprocess_text),
                         tokens=lambda x: x['cleaned_description'].apply(
                             lambda text: tokenize_and_filter(text, stop_words))))
    
    all_tokens = df_filtered['tokens'].explode().tolist()
    word_counts = Counter(all_tokens)
    
    return word_counts.most_common(10), all_tokens

def extract_single_stage(text: str, pattern: str, 
                        language: str, context_patterns: Dict[str, str]) -> str:
    '''Extract text around interview stage pattern.'''
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

def extract_interview_details(df: pd.DataFrame, column: str, 
                            language_column: str = 'language') -> Tuple[pd.DataFrame, pd.DataFrame]:
    '''Extract interview process details from job descriptions.'''
    base_df = df[['job_id', 'search_keyword', 'job_link', language_column]].copy()
    
    bounded_patterns = {
        stage: '|'.join(fr'\b{p}\b' for p in pattern.split('|'))
        for stage, pattern in INTERVIEW_STAGES.items()
    }
    
    for stage, pattern in bounded_patterns.items():
        base_df[f'{stage}_text'] = df.apply(
            lambda row: extract_single_stage(
                row[column], pattern, row[language_column], CONTEXT_PATTERNS),
            axis=1)
        base_df[stage] = base_df[f'{stage}_text'].notna()
    
    text_columns = ['job_id', 'search_keyword', 'job_link'] + [f'{s}_text' for s in INTERVIEW_STAGES]
    flag_columns = ['job_id', 'search_keyword', 'job_link'] + list(INTERVIEW_STAGES.keys())
    
    return base_df[text_columns], base_df[flag_columns]