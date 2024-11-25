import pandas as pd

def desc_categorical(data: pd.DataFrame) -> None:
    '''Prints value counts for categorical columns in the given DataFrame.'''
    # Exclude these 
    string_columns = data.select_dtypes(include='string').drop(columns=['job_description', 'job_description_norm'])
    object_columns = data.select_dtypes(include='object').drop(columns='job_link')
    for col in string_columns.columns:
        print(f"Value counts for column: {col}\n{string_columns[col].value_counts()}\n")
    for col in object_columns.columns:
        print(f"Value counts for column: {col}\n{object_columns[col].value_counts()}\n")

def get_top_skills_by_job(df: pd.DataFrame, n_skills: int = 20, by_country: bool = False) -> pd.DataFrame:
    '''
    Get top n skills for each job type, optionally split by country.
    
    Args:
        df: DataFrame with columns ['Search Keyword', 'Keyword', 'Category', 'Count']
        n_skills: Number of top skills to return for each job type (default: 10)
        by_country: Whether to analyze separately by country (default: False)
    
    Returns:
        DataFrame with top skills per job type
    '''
    index = ['Search Keyword', 'Keyword', 'Category']
    groupby = ['Search Keyword']
    sort_by = ['Search Keyword', 'Count']
    sort_ascending = [True, False]  # Changed this line
    
    if by_country:
        index = ['Search Keyword', 'Country', 'Keyword', 'Category']
        groupby = ['Search Keyword', 'Country']
        sort_by = ['Search Keyword', 'Country', 'Count']
        sort_ascending = [True, True, False]  # Changed this line
    
    # Aggregate counts
    df = df.pivot_table(
        index=index,
        values='Count',
        aggfunc='sum',
        observed=True
    )
    
    # Reset index to get columns back
    df = df.reset_index()
    
    # Add rank within groups
    df = df.assign(
        rank=lambda x: x.groupby(groupby, observed=True)['Count']
        .rank(method='dense', ascending=False)
    )
    
    # Filter to top n_skills
    df = df.query(f'rank <= {n_skills}')
    
    # Sort values with specified ascending/descending
    df = df.sort_values(sort_by, ascending=sort_ascending) 
    
    # Drop rank column
    df = df.drop('rank', axis=1)
    
    return df

def display_top_skills(df: pd.DataFrame) -> None:
    '''
    Display top skills from the DataFrame returned by get_top_skills_by_job.
    
    Args:
        df: DataFrame with columns including Search Keyword, Keyword, Count, Category
            (and optionally Country)
    '''
    has_country = 'Country' in df.columns
    columns_to_show = ['Keyword', 'Count', 'Category']
    
    for job in df['Search Keyword'].unique():
        if has_country:
            for country in df['Country'].unique():
                print(f"\n\nTop skills for {job} in {country}:")
                mask = (df['Search Keyword'] == job) & (df['Country'] == country)
                print(df[mask][columns_to_show].to_string())
        else:
            print(f"\n\nTop skills for {job}:")
            print(df[df['Search Keyword'] == job][columns_to_show].to_string())