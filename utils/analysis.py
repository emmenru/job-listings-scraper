import re
from itertools import combinations

import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from scipy.stats import kruskal, mannwhitneyu, shapiro, levene

from utils.dictionaries import COUNTRIES_LANGUAGES, SOFTWARE_KEYWORDS, COUNTRY_CODE_MAP

def desc_categorical(data: pd.DataFrame) -> None:
   '''Print value counts for categorical columns.'''
   string_cols = data.select_dtypes(include='string').drop(columns=['job_description', 'job_description_norm'])
   object_cols = data.select_dtypes(include='object').drop(columns='job_link')
   
   for col in string_cols.columns:
       print(f'Value counts for column: {col}\n{string_cols[col].value_counts()}\n')
   for col in object_cols.columns:
       print(f'Value counts for column: {col}\n{object_cols[col].value_counts()}\n')

def count_keywords(df: pd.DataFrame, country: str, job_description_col: str) -> pd.DataFrame:
   '''Count keyword occurrences in job descriptions for given country.'''
   df_filtered = df[df['country'] == country].copy()
   df_filtered[job_description_col] = df_filtered[job_description_col].str.lower()
   
   keyword_df = pd.DataFrame([
       (category, keyword) 
       for category, keywords in SOFTWARE_KEYWORDS.items()
       for keyword in keywords],
       columns=['Category', 'Keyword'])
   
   result = (df_filtered[[job_description_col, 'search_keyword']]
            .assign(key=1)
            .merge(keyword_df.assign(key=1), on='key')
            .drop('key', axis=1))

   result['Count'] = result.apply(lambda row: 1 if re.search(fr'\b{row["Keyword"]}\b', row[job_description_col], re.IGNORECASE) else 0, axis=1)
   
   result = (result[result['Count'] > 0]
            .assign(Country=country)[['Category', 'Keyword', 'Count', 'search_keyword', 'Country']]
            .rename(columns={'search_keyword': 'Search Keyword'}))
   
   return result.groupby(['Category', 'Keyword', 'Search Keyword', 'Country'], observed=True).sum().reset_index()

def calculate_country_frequencies(technical_skills: pd.DataFrame, df_combined: pd.DataFrame) -> pd.DataFrame:
   '''Calculate keyword frequencies by country relative to total job listings.'''
   total_jobs_by_country = df_combined.groupby('country', observed=True).size().reset_index(name='Total_jobs')
   country_keyword_counts = technical_skills.groupby(['Country', 'Category', 'Keyword'], observed=True)['Count'].sum().reset_index()
   
   results_with_freq = (country_keyword_counts
                       .merge(total_jobs_by_country, left_on='Country', right_on='country')
                       .assign(Frequency=lambda x: (x['Count'] / x['Total_jobs'] * 100).round(2))
                       .drop('country', axis=1))
   
   return results_with_freq.sort_values(['Country', 'Frequency'], ascending=[True, False])

def calculate_global_frequencies(technical_skills: pd.DataFrame, df_combined: pd.DataFrame) -> pd.DataFrame:
   '''Calculate global keyword frequencies across all countries and search terms.'''
   total_jobs = len(df_combined)
   global_counts = (technical_skills
                   .groupby(['Category', 'Keyword'], observed=True)['Count']
                   .sum()
                   .reset_index()
                   .assign(Frequency=lambda x: (x['Count'] / total_jobs * 100).round(2),
                          Total_jobs=total_jobs)
                   .sort_values('Frequency', ascending=False))
   
   return global_counts

def calculate_frequencies_by_search_keyword(technical_skills: pd.DataFrame, df_combined: pd.DataFrame) -> pd.DataFrame:
   '''Calculate keyword frequencies by search term across all countries.'''
   total_jobs_by_search = df_combined.groupby('search_keyword', observed=True).size().reset_index(name='Total_jobs')
   search_keyword_counts = technical_skills.groupby(['Search Keyword', 'Category', 'Keyword'], observed=True)['Count'].sum().reset_index()
   
   results_with_freq = (search_keyword_counts
                       .merge(total_jobs_by_search, left_on='Search Keyword', right_on='search_keyword')
                       .assign(Frequency=lambda x: (x['Count'] / x['Total_jobs'] * 100).round(2))
                       .drop('search_keyword', axis=1)
                       .sort_values(['Search Keyword', 'Frequency'], ascending=[True, False]))
   
   return results_with_freq

def check_anova_assumptions(model, df: pd.DataFrame, group1: str, group2: str, value_column: str) -> None:
   '''Check Two-Way ANOVA assumptions: normality and homogeneity of variance.'''
   residuals = model.resid
   stats.probplot(residuals, dist='norm', plot=plt)
   plt.title('Q-Q plot')
   plt.show()
  
   stat, p = shapiro(residuals)
   print(f'Shapiro-Wilk test:\nStatistic: {stat:.4f}\np-value: {p:.2e}')
  
   groups1 = [group[value_column] for _, group in df.groupby(group1, observed=True)]
   lev1_stat, lev1_p = levene(*groups1)
   print(f'\nLevene test for {group1}:\nStatistic: {lev1_stat:.4f}\np-value: {lev1_p:.2e}')
  
   groups2 = [group[value_column] for _, group in df.groupby(group2, observed=True)]
   lev2_stat, lev2_p = levene(*groups2)
   print(f'\nLevene test for {group2}:\nStatistic: {lev2_stat:.4f}\np-value: {lev2_p:.2e}')

def run_mann_whitney_analysis(df: pd.DataFrame, group_column: str, value_column: str) -> None:
   '''Run Mann-Whitney U tests with Bonferroni correction after significant Kruskal-Wallis.'''
   groups = [group[value_column] for name, group in df.groupby(group_column, observed=True)]
   stat, p = kruskal(*groups)
   print(f'Kruskal-Wallis test:\nStatistic: {stat:.2f}\np-value: {p:.2e}\n')
  
   categories = df[group_column].unique()
   n_combinations = len(list(combinations(categories, 2)))
  
   for a, b in combinations(categories, 2):
       group1 = df[df[group_column]==a][value_column]
       group2 = df[df[group_column]==b][value_column]
       stat, p = mannwhitneyu(group1, group2)
       p_adjusted = p * n_combinations
       print(f'{a} vs {b}: p={p_adjusted:.4f}')
  
   print('\nMedian values:')
   print(df.groupby(group_column, observed=True)[value_column].median())
   print('--------\n')