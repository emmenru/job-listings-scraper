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
    group['normalized_text'] = group['job_description'].apply(lambda x: normalize_text(x, group.name, dicts.language_map))
    return group

########## Old code below

def tokenize_and_filter(text, stop_words):
    # Tokenization: split text into words and remove stopwords
    tokens = text.split()
    return [word for word in tokens if word not in stop_words]
 
def preprocess_text(text):
    # Remove punctuation and make lowercase
    return re.sub(r'[^\w\s]', '', text.lower())

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
    
    # Always include English stopwords
    stop_words = set(stopwords.words('english'))

    # Add additional stopwords based on the specified language
    if language == 'french':
        stop_words.update(stopwords.words('french'))
    elif language == 'italian':
        stop_words.update(stopwords.words('italian'))
    elif language == 'swedish':
        stop_words.update(stopwords.words('swedish'))
    elif language == 'english':
        # English stopwords are already included at the top
        pass
    else:
        raise ValueError("Unsupported language.")

    # Filter the DataFrame for the specified country
    df_country = df[df['country'] == country].copy()  # Create a copy to avoid SettingWithCopyWarning

    # Use .loc to assign new columns
    df_country.loc[:, 'cleaned_description'] = df_country['job_description'].apply(preprocess_text)
    #df_country.loc[:, 'tokens'] = df_country['cleaned_description'].apply(tokenize_and_filter)
    df_country.loc[:, 'tokens'] = df_country['cleaned_description'].apply(lambda text: tokenize_and_filter(text, stop_words))

    # Flatten the list of tokens and count frequencies
    all_tokens = [token for sublist in df_country['tokens'] for token in sublist]
    word_counts = Counter(all_tokens)

    # Get the top 10 keywords
    common_keywords = word_counts.most_common(10)  
    return (common_keywords, all_tokens)

def count_keywords(df, country, software_keywords):
    """
    Counts the occurrences of keywords in job descriptions for a specific country and categorizes them.

    Args:
        df: The DataFrame containing job descriptions and search keywords.
        country: The country to filter the data by.
        software_keywords: A dictionary mapping categories to lists of keywords.

    Returns:
        A DataFrame with columns for category, keyword, count, associated search keyword, and country.
    """
    # Prepare the DataFrame list to store individual entries
    data = []

    # Filter DataFrame by country
    filtered_df = df[df['country'] == country]
    
    # Flatten the keywords into a single list with their categories
    category_keywords = [(category, keyword) for category, keywords in software_keywords.items() for keyword in keywords]

    for index, row in filtered_df.iterrows():
        job_description = row['job_description'].lower()  # Access job description
        search_keyword = row['search_keyword']  # Access associated search keyword
        
        for category, keyword in category_keywords:
            count = job_description.count(keyword)
            if count > 0:  # Only record non-zero counts
                data.append({
                    'Category': category,
                    'Keyword': keyword,
                    'Count': count,
                    'Search Keyword': search_keyword,
                    'Country': country  
                })

    # Create a df from the collected data
    result_df = pd.DataFrame(data)

    # Group by relevant columns and sum the counts
    result_df = result_df.groupby(['Category', 'Keyword', 'Search Keyword', 'Country'], as_index=False).sum()

    return result_df


def extract_stage_text(job_desc, stage_pattern, context_window=100):
    """
    Extracts text related to the interview process from a job description.

    Args:
        job_desc: The text of the job description.
        stage_pattern: A string or raw string pattern representing an interview stage (e.g., "phone interview").
        context_window: The number of characters to capture around the matched stage pattern (default: 100).

    Returns:
        A string containing the extracted text surrounding the stage pattern within the interview process context, 
        or None if no match is found.
    """
    # Define the context pattern as a constant here
    context_pattern = r'recruitment process|interview process'

    # First, find the location of the context pattern
    context_match = re.search(context_pattern, job_desc, re.IGNORECASE)
    
    if context_match:
        # Narrow down the text to start after the context pattern match
        context_start = context_match.end()
        text_after_context = job_desc[context_start:]
        
        # Now, search for the stage pattern within this limited text
        stage_match = re.search(stage_pattern, text_after_context, re.IGNORECASE)
        
        if stage_match:
            # Calculate the adjusted start and end based on `text_after_context`
            start = max(0, stage_match.start() - 20)
            end = min(len(text_after_context), stage_match.end() + context_window)
            
            # Print the extracted text
            extracted_text = text_after_context[start:end].strip()
            #print("----Extracted Text Around Stage Pattern----")
            #print(extracted_text)
            return extracted_text  # Return the extracted text
            
    return None  # Return None if no match is found
    
def extract_interview_details(df, stages):
    """
    Extracts detailed information about interview stages from job descriptions and creates two DataFrames.

    Args:
        df: The DataFrame containing job descriptions and other relevant information.
        stages: Dictionary with fefined patterns for each interview stage.
    
    Returns:
        A tuple of two DataFrames:
        1. Detailed text DataFrame: Contains extracted text for each interview stage, along with job ID, title, and link.
        2. Boolean indicator DataFrame: Indicates the presence of each interview stage with True/False values.
    """
    interview_info = []
    interview_flags = []

    for _, row in df.iterrows():
        job_desc = row['job_description']
        
        # Store detailed text and flags for each stage in dictionaries
        details = {
            'job_id': row['job_id'],
            'job_title': row['job_title'],     # Add job title
            'job_link': row['job_link']        # Add job link or other useful identifiers
        }
        flags = {
            'job_id': row['job_id'],
            'job_title': row['job_title'],
            'job_link': row['job_link']
        }
        
        for stage, pattern in stages.items():
            extracted_text = extract_stage_text(job_desc, pattern)
            details[f'{stage}_text'] = extracted_text
            flags[stage] = bool(extracted_text)
        
        interview_info.append(details)
        interview_flags.append(flags)

    # Convert the lists of dictionaries into DataFrames
    interview_info_df = pd.DataFrame(interview_info)
    interview_flags_df = pd.DataFrame(interview_flags)

    return interview_info_df, interview_flags_df