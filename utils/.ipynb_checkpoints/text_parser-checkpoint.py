import re
import string
from collections import Counter

import nltk
import pandas as pd
from langdetect import LangDetectException, detect
from nltk import download
from nltk.corpus import stopwords

import utils.dictionaries as dicts

downloaded_stopwords = {}
PUNCT_REGEX = r'[^\w\s]'
STOPWORD_MAP = {
    'french': lambda: stopwords.words('english') + stopwords.words('french'), 
    'italian': lambda: stopwords.words('english') + stopwords.words('italian'),
    'swedish': lambda: stopwords.words('english') + stopwords.words('swedish'), 
    'english': lambda: stopwords.words('english'),
}

def download_stopwords(language: str) -> None:
    '''Download stopwords for given language if not already downloaded.'''
    global downloaded_stopwords
    if language not in downloaded_stopwords:
        download('punkt', quiet=True)
        download('wordnet', quiet=True)
        downloaded_stopwords[language] = set(stopwords.words(language))
        

def tokenize_and_filter(text: str, stop_words: set) -> list:
    '''Tokenize text and filter out stopwords.'''
    tokens = text.split()
    return [token for token in tokens if token not in stop_words]


def preprocess_text(text: str) -> str:
    '''Remove punctuation and lowercase text.'''
    return re.sub(PUNCT_REGEX, '', text.lower())


def detect_language(text: str) -> str:
    '''Detect language of given text.'''
    try:
        return detect(text)
    except LangDetectException:
        return 'Unknown'


def normalize_text(text: str, language_code: str, language_map: dict) -> str:
    '''Normalize text by lowercasing, lemmatizing, and removing stopwords.'''
    language = language_map.get(language_code, 'Unknown')
    download_stopwords(language)

    text = text.lower() 
    words = tokenize_and_filter(text, downloaded_stopwords.get(language, set()))
    words = [word.strip(string.punctuation) for word in words]

    lemmatizer = nltk.WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
             
    return ' '.join(words)


def normalize_group(group: pd.DataFrame) -> pd.DataFrame:
    '''Normalize job description text for a language group.'''  
    print(f'Normalizing text for language group: {group.name}')
    group['job_description_norm'] = group['job_description'].apply(
        lambda x: normalize_text(x, group.name, dicts.language_map),
    )
    return group


def extract_keywords(
    df: pd.DataFrame, 
    country: str,
    language: str,
) -> tuple:
    '''Extract top keywords from job descriptions for given country/language.
    
    Args:
        df: DataFrame with job descriptions. 
        country: Country to analyze.
        language: Language of job descriptions.
        
    Returns:
        Tuple of top 10 keywords and list of all tokens.
    '''
    job_description_col = 'job_description_norm'
    
    try:
        stop_words = set(STOPWORD_MAP[language]())
    except KeyError:
        raise ValueError(f'Unsupported language: {language}')
        
    df_filtered = (
        df[df['country'] == country]
        .assign(
            cleaned_description=lambda x: x[job_description_col].apply(
                preprocess_text,
            ),
            tokens=lambda x: x['cleaned_description'].apply(
                lambda text: tokenize_and_filter(text, stop_words),
            ),
        )
    )
    
    all_tokens = df_filtered['tokens'].explode().tolist()
    word_counts = Counter(all_tokens)
    
    return word_counts.most_common(10), all_tokens


def count_keywords(
    df: pd.DataFrame,
    country: str, 
    software_keywords: dict,
    job_description_col: str,
) -> pd.DataFrame:
    '''Count occurrences of predefined keyword categories in job descriptions.
    
    Args:
        df: DataFrame with job descriptions and metadata.
        country: Country to analyze.  
        software_keywords: Dict mapping keyword categories to keyword lists.
        job_description_col: Column containing job description text.
        
    Returns:    
        DataFrame with keyword counts by category/country.
    '''
    df_filtered = df[df['country'] == country].copy()
    df_filtered[job_description_col] = df_filtered[job_description_col].str.lower()
    
    keyword_df = pd.DataFrame(
        [
            (category, keyword) 
            for category, keywords in software_keywords.items()
            for keyword in keywords  
        ],
        columns=['Category', 'Keyword'],
    )
    
    result = (  
        df_filtered[[job_description_col, 'search_keyword']]
        .assign(key=1)
        .merge(keyword_df.assign(key=1), on='key') 
        .drop('key', axis=1)
    )
    
    result['Count'] = result.apply(
        lambda row: 1 if row['Keyword'] in row[job_description_col] else 0,
        axis=1,  
    )
    
    result = (
        result[result['Count'] > 0]
        .assign(Country=country)  
        [['Category', 'Keyword', 'Count', 'search_keyword', 'Country']]
        .rename(columns={'search_keyword': 'Search Keyword'})
    )
    
    return ( 
        result.groupby(
            ['Category', 'Keyword', 'Search Keyword', 'Country'],
            observed=True,
        )
        .sum()
        .reset_index()
    )


def extract_single_stage(
    text: str,
    pattern: str, 
    language: str,
    context_patterns: dict,  
) -> str:
    '''Extract text around a given pattern from job description.'''
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


def extract_interview_details(
    df: pd.DataFrame, 
    stages: dict,
    context_patterns: dict,  
    column: str,
    language_column: str = 'language',  
) -> tuple:
    '''Extract details on interview stages from job descriptions.
    
    Args:
        df: DataFrame with job descriptions and metadata.  
        stages: Dict of regex patterns for each interview stage.
        context_patterns: Dict of context patterns by language. 
        column: Column containing job description text.
        language_column: Column specifying description language.
        
    Returns:
        Tuple of DataFrames with extracted stage text and boolean stage indicators.
    '''
    base_df = df[['job_id', 'search_keyword', 'job_link', language_column]].copy()
    
    for stage, pattern in stages.items():
        base_df[f'{stage}_text'] = df.apply( 
            lambda row: extract_single_stage(
                row[column], pattern, row[language_column], context_patterns,
            ),
            axis=1,
        )
        base_df[stage] = base_df[f'{stage}_text'].notna()
        
    text_columns = ['job_id', 'search_keyword', 'job_link'] + [
        f'{s}_text' for s in stages
    ]
    flag_columns = ['job_id', 'search_keyword', 'job_link'] + list(stages.keys())
    
    return base_df[text_columns], base_df[flag_columns]