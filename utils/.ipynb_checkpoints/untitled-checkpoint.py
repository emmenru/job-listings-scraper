import pandas as pd

def get_top_skills_by_job(df, n_skills=10):
    """
    Get top n skills for each job type across all countries.
    
    Args:
        df: DataFrame with columns ['Search Keyword', 'Keyword', 'Category', 'Count']
        n_skills: Number of top skills to return for each job type (default: 10)
    
    Returns:
        DataFrame with top skills per job type
    """
    return (df
            .pivot_table(
                index=['Search Keyword', 'Keyword', 'Category'],
                values='Count',
                aggfunc='sum'
            )
            .reset_index()
            .assign(
                rank=lambda x: x.groupby('Search Keyword')['Count']
                .rank(method='dense', ascending=False)
            )
            .query(f'rank <= {n_skills}')
            .sort_values(['Search Keyword', 'Count'], ascending=[True, False])
            .drop('rank', axis=1))

def get_top_skills_by_job_and_country(df, n_skills=10):
    """
    Get top n skills for each job type by country.
    
    Args:
        df: DataFrame with columns ['Search Keyword', 'Keyword', 'Category', 'Count', 'Country']
        n_skills: Number of top skills to return for each combination (default: 10)
    
    Returns:
        DataFrame with top skills per job type and country
    """
    return (df
            .pivot_table(
                index=['Search Keyword', 'Country', 'Keyword', 'Category'],
                values='Count',
                aggfunc='sum'
            )
            .reset_index()
            .assign(
                rank=lambda x: x.groupby(['Search Keyword', 'Country'])['Count']
                .rank(method='dense', ascending=False)
            )
            .query(f'rank <= {n_skills}')
            .sort_values(['Search Keyword', 'Country', 'Count'], 
                        ascending=[True, True, False])
            .drop('rank', axis=1))

def display_top_skills(df, by_country=False):
    """
    Display top skills in a formatted way.
    
    Args:
        df: DataFrame with top skills
        by_country: Whether to group by country as well (default: False)
    """
    if by_country:
        for job in df['Search Keyword'].unique():
            for country in df['Country'].unique():
                print(f"\n\nTop skills for {job} in {country}:")
                mask = (df['Search Keyword'] == job) & (df['Country'] == country)
                print(df[mask][['Keyword', 'Count', 'Category']].to_string())
    else:
        for job in df['Search Keyword'].unique():
            print(f"\n\nTop skills for {job}:")
            print(df[df['Search Keyword'] == job]
                  [['Keyword', 'Count', 'Category']].to_string())
