import pandas as pd

from utils.dictionaries import COUNTRIES_LANGUAGES, SOFTWARE_KEYWORDS, COUNTRY_CODE_MAP 

def desc_categorical(data: pd.DataFrame) -> None:
    '''Prints value counts for categorical columns in the given DataFrame.'''
    # Exclude these 
    string_columns = data.select_dtypes(include='string').drop(columns=['job_description', 'job_description_norm'])
    object_columns = data.select_dtypes(include='object').drop(columns='job_link')
    for col in string_columns.columns:
        print(f"Value counts for column: {col}\n{string_columns[col].value_counts()}\n")
    for col in object_columns.columns:
        print(f"Value counts for column: {col}\n{object_columns[col].value_counts()}\n")

#def count_keywords(df: pd.DataFrame, country: str, software_keywords: dict, job_description_col: str, ) -> pd.DataFrame:
def count_keywords(df: pd.DataFrame, country: str, job_description_col: str) -> pd.DataFrame:
    '''Count occurrences of keyword and categories in job descriptions.
    
    Args:
        df: DataFrame with job descriptions and metadata.
        country: Country to analyze.  
        software_keywords: Dict mapping keyword categories to keyword lists.
        job_description_col: Column containing job description text.
        
    Returns:    
        DataFrame with keyword counts by category/country.

    Please note: 
        For later calculation of relative frequency: note that the total number of job listings will be different from the sum of the counts here.
        A single job listing can contain multiple keywords (e.g., a job might require both 'python' and 'sql'). 
        The same job listing will be counted multiple times if it contains multiple keywords. 
    '''
    df_filtered = df[df['country'] == country].copy()
    df_filtered[job_description_col] = df_filtered[job_description_col].str.lower()
    keyword_df = pd.DataFrame([
        (category, keyword) 
        for category, keywords in SOFTWARE_KEYWORDS.items()
        for keyword in keywords],
                            columns=['Category', 'Keyword'])
    
    #df_filtered = df[df['country'] == country].copy()
    #df_filtered[job_description_col] = df_filtered[job_description_col].str.lower()
    
    #keyword_df = pd.DataFrame([
    #        (category, keyword) 
    #        for category, keywords in software_keywords.items()
    #        for keyword in keywords],
    #    columns=['Category', 'Keyword'],)
    
    result = (df_filtered[[job_description_col, 'search_keyword']].assign(key=1).merge(keyword_df.assign(key=1), on='key') .drop('key', axis=1))
    
    result['Count'] = result.apply(lambda row: 1 if row['Keyword'] in row[job_description_col] else 0,axis=1,)
    
    result = (result[result['Count'] > 0].assign(Country=country)[['Category', 'Keyword', 'Count', 'search_keyword', 'Country']].rename(columns={'search_keyword': 'Search Keyword'}))
    
    return (result.groupby(['Category', 'Keyword', 'Search Keyword', 'Country'], observed=True,).sum().reset_index())

def calculate_country_frequencies(technical_skills: pd.DataFrame, df_combined: pd.DataFrame) -> pd.DataFrame:
    '''
    Calculate keyword frequencies relative to total job listings per country (regardless of search keyword).
    
    Args:
        technical_skills: DataFrame with keyword counts
        df_combined: Original DataFrame with all job listings
    
    Returns:
        DataFrame with country-specific counts and frequencies
    '''
    # Calculate total jobs per country (ignoring search keyword)
    total_jobs_by_country = (df_combined.groupby('country', observed=True).size().reset_index(name='Total_jobs'))
    
    # Sum counts by country and keyword
    country_keyword_counts = (technical_skills.groupby(['Country', 'Category', 'Keyword'], observed=True)['Count'].sum().reset_index())
    
    # Calculate frequencies
    results_with_freq = (country_keyword_counts.merge(total_jobs_by_country,left_on='Country',right_on='country').assign(Frequency=lambda x: (x['Count'] / x['Total_jobs'] * 100).round(2)).drop('country', axis=1))
    
    return results_with_freq.sort_values(['Country', 'Frequency'], ascending=[True, False])

def calculate_global_frequencies(technical_skills: pd.DataFrame, df_combined: pd.DataFrame) -> pd.DataFrame:
    '''
    Calculate global keyword frequencies across all countries and search keywords.
    
    Args:
        technical_skills: DataFrame with keyword counts
        df_combined: Original DataFrame with all job listings
    
    Returns:
        DataFrame with global counts and frequencies for each skill
    '''
    # Calculate total number of jobs across everything
    total_jobs = len(df_combined)
    
    # Sum counts across all countries and search keywords
    global_counts = (technical_skills.groupby(['Category', 'Keyword'], observed=True)['Count'].sum().reset_index().assign(Frequency=lambda x: (x['Count'] / total_jobs * 100).round(2),Total_jobs=total_jobs).sort_values('Frequency', ascending=False))
    
    return global_counts

def calculate_frequencies_by_search_keyword(technical_skills: pd.DataFrame, df_combined: pd.DataFrame) -> pd.DataFrame:
    '''
    Calculate keyword frequencies for each search keyword across all countries.
    
    Args:
        technical_skills: DataFrame with keyword counts
        df_combined: Original DataFrame with all job listings
    
    Returns:
        DataFrame with counts and frequencies by search keyword
    '''
    # Calculate total jobs per search keyword
    total_jobs_by_search = (df_combined.groupby('search_keyword', observed=True).size().reset_index(name='Total_jobs'))
    
    # Sum counts across countries for each search keyword and keyword
    search_keyword_counts = (technical_skills.groupby(['Search Keyword', 'Category', 'Keyword'], observed=True)['Count'].sum().reset_index())
    
    # Calculate frequencies
    results_with_freq = (search_keyword_counts.merge(total_jobs_by_search,left_on='Search Keyword',right_on='search_keyword').assign(Frequency=lambda x: (x['Count'] / x['Total_jobs'] * 100).round(2)).drop('search_keyword', axis=1).sort_values(['Search Keyword', 'Frequency'], ascending=[True, False]))
    
    return results_with_freq
