import re
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

def detect_outliers(df: pd.DataFrame, numerical_cols: List[str]) -> Tuple[Dict, List]:
    '''Detect outliers using IQR method.'''
    outlier_info = {}
    outliers_data = []
    
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = max(0, Q1 - 1.5 * IQR)
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outliers = df[col][outlier_mask]

        for idx in outliers.index:
            outlier_info[idx] = outlier_info.get(idx, []) + ['min salary' if 'min' in col else 'max salary']
            
        outliers_data.extend([(col, value) for value in outliers])
        
        print(f'\nOutliers for {col}:')
        print(f'Number of outliers: {len(outliers)}')
        print('Outlier values:')
        for value in sorted(outliers.values):
            print(f'€{value:,.2f}')
        print(f'Lower bound: €{lower_bound:,.2f}')
        print(f'Upper bound: €{upper_bound:,.2f}')
    
    return outlier_info, outliers_data

def plot_boxplot(df: pd.DataFrame, numerical_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    '''Plot and identify outliers in numerical columns using boxplots.'''
    plt.figure(figsize=(5, 3))
    melted_df = df[numerical_cols].melt(var_name='Variable', value_name='EUR per month')
    print('Shape of melted data:', melted_df.shape)
    print('Number of non-null values per column:')
    print(melted_df.count())
    
    sns.boxplot(data=melted_df, x='Variable', y='EUR per month', width=0.2, 
                color='mediumseagreen', showfliers=False)
    
    outlier_info, outliers_data = detect_outliers(df, numerical_cols)
    outliers_df = pd.DataFrame(outliers_data, columns=['Variable', 'EUR per month']) if outliers_data else pd.DataFrame()
    
    if not outliers_df.empty:
        sns.stripplot(data=outliers_df, x='Variable', y='EUR per month',
                     color='darkgreen', size=6, alpha=0.6, jitter=0.2)
    
    plt.title('Min vs Max Salary')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    original_rows = df.loc[list(outlier_info.keys())].copy()
    original_rows['outlier_source'] = [','.join(sources) for sources in outlier_info.values()]
    
    return outliers_df, original_rows

def plot_grouped_histograms(df: pd.DataFrame, group_col: str, value_col: str, bins: int = 10, 
                          kde: bool = True, figsize: Tuple[int, int] = (16, 6), 
                          title: str = 'Histogram') -> None:
    '''Plot histograms for numerical column grouped by categories.'''
    unique_groups = df[group_col].unique()
    fig, axes = plt.subplots(1, len(unique_groups), figsize=figsize)

    for i, group in enumerate(unique_groups):
        group_data = df[df[group_col] == group]
        sns.histplot(x=value_col, data=group_data, bins=bins, kde=kde,
                    alpha=0.5, color='mediumseagreen', ax=axes[i])
        axes[i].set_title(group)
        axes[i].set_xlabel('EUR')
        axes[i].set_ylabel('Frequency')

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

def plot_grouped_bar(df: pd.DataFrame, group_col: str, value_col: str, 
                    figsize: Tuple[int, int] = (16, 10), title: str = 'Bar Plot', 
                    top_n: int = 10, ylim: int = 700) -> None:
    '''Plot grouped bar charts with top N categories.'''
    unique_groups = df[group_col].unique()
    fig, axes = plt.subplots(1, len(unique_groups), figsize=figsize)

    for i, group in enumerate(unique_groups):
        group_data = df[df[group_col] == group]
        top_categories = group_data[value_col].value_counts().nlargest(top_n)

        sns.countplot(data=group_data, x=value_col, order=top_categories.index,
                     color='mediumseagreen', ax=axes[i], width=0.5)
        axes[i].set_title(group)
        for label in axes[i].get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        axes[i].set_xlabel('')
        axes[i].set_ylim(0, ylim)

    plt.suptitle(title)
    plt.show()

def plot_salary_by_keyword(df: pd.DataFrame, figsize: Tuple[int, int] = (5, 4)) -> None:
    '''Create boxplot of salaries by search keyword for France.'''
    plt.figure(figsize=figsize)
    
    sns.boxplot(data=df.query("country == 'France'"),
                x='search_keyword', y='max_salary_month_EUR',
                color='mediumseagreen', width=0.25)
    
    plt.xlabel('Job Title')
    plt.ylabel('Maximum Monthly Salary (EUR)')
    plt.title('Salary Distribution by Job Title in France')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_box(df: pd.DataFrame, y: str = 'max_salary_month_EUR',
            x: str = 'region', hue: str = 'job_title',
            figsize: Tuple[int, int] = (10, 6)) -> None:
    '''Create boxplot showing salary distribution by location and job title.'''
    plt.figure(figsize=figsize)
    sns.boxplot(data=df, x=x, y=y, hue=hue, width=0.8)
    
    plt.xlabel('Company Location')
    plt.ylabel('Maximum Monthly Salary (EUR)')
    plt.title('Salary Distribution by Job Title and Location')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def plot_skills_bars(df: pd.DataFrame, figsize: Tuple[int, int] = (15, 8)) -> None:
    '''Create grouped bar chart of skills frequency by role.'''
    plt.figure(figsize=figsize)
    
    skill_order = (df.groupby('Keyword')['Frequency']
                   .mean()
                   .sort_values(ascending=False)
                   .index)
    
    sns.barplot(data=df, x='Keyword', y='Frequency', hue='Search Keyword',
                palette='Set2', order=skill_order)
    
    plt.title('Required Skills Frequency by Role')
    plt.xlabel('Skill')
    plt.ylabel('Frequency (%)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Role', bbox_to_anchor=(1.05, 1))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_common_keywords(common_keywords: List[Tuple], country: str) -> None:
    '''Create bar chart of common keywords in job descriptions.'''
    words, counts = zip(*common_keywords)
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='mediumseagreen')
    plt.xlabel('Keywords', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.title(f'Most Common Keywords in Job Descriptions - {country}', fontsize=16)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_wordtree(data: List[str], country: str, figsize: Tuple[int, int] = (10, 5),
                 width: int = 800, height: int = 400, 
                 background_color: str = 'white') -> None:
    '''Create word cloud visualization from text descriptions.'''
    text = ' '.join(data)
    wordcloud = WordCloud(width=width, height=height, 
                         background_color=background_color).generate(text)
    
    plt.figure(figsize=figsize)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title(f'Wordcloud of Job Descriptions - {country}')
    plt.axis('off')
    plt.show()

def plot_stacked_bar_chart(df: pd.DataFrame, title: str = 'Stacked Bar Chart of Categories by Search Keyword',
                          colormap: str = 'gist_ncar', 
                          figsize: Tuple[int, int] = (16, 10)) -> None:
    '''Create stacked bar chart of category distribution by search keyword.'''
    (df.pivot_table(index='Search Keyword', columns='Category', 
                   values='Count', aggfunc='sum', observed=True)
       .fillna(0)
       .plot(kind='bar', stacked=True, colormap=colormap,
             edgecolor='black', figsize=figsize))
    
    plt.title(title, fontsize=16, pad=20)
    plt.xlabel('Search Keyword', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.xticks(rotation=90, fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), 
              loc='upper left', fontsize=12)
    plt.tight_layout()
    plt.show()

def plot_top_keyword_heatmap(df: pd.DataFrame, top_n: int = 15,
                            figsize: Tuple[int, int] = (15, 10),
                            title: str = 'Top Keyword Distribution Across Job Titles') -> None:
    '''Create heatmap of top N keywords across job titles.'''
    top_combinations = (df.groupby(['Category', 'Keyword', 'Search Keyword'], observed=True)['Count']
                       .sum()
                       .reset_index()
                       .pipe(lambda x: x.merge(
                           x.groupby(['Category', 'Keyword'])['Count']
                           .sum()
                           .nlargest(top_n)
                           .reset_index()[['Category', 'Keyword']], 
                           on=['Category', 'Keyword']))
                       .pivot(index='Search Keyword', columns='Keyword', values='Count'))
    
    plt.figure(figsize=figsize)
    sns.heatmap(top_combinations, annot=True, fmt='.0f',
                cmap='YlOrRd', cbar_kws={'label': 'Count'})
    
    plt.title(title, pad=20)
    plt.xlabel('Skill', fontsize=12)
    plt.ylabel('Role', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_keywords_per_group_subplots(df: pd.DataFrame, group_col: str, 
                                   keyword_col: str, count_col: str,
                                   n_top: int = 5, 
                                   figsize: Tuple[int, int] = (16, 12)) -> None:
    '''Create subplots showing top N keywords for each group.'''
    groups = df[group_col].unique()
    n_cols = 3
    n_rows = -(-len(groups) // n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    for i, (group, ax) in enumerate(zip(groups, axes.flatten())):
        group_data = df[df[group_col] == group]
        top_keywords = (group_data.groupby(keyword_col)[count_col]
                       .sum()
                       .nlargest(n_top)
                       .reset_index())

        sns.barplot(data=top_keywords, x=count_col, y=keyword_col,
                   color='mediumseagreen', ax=ax)
        
        ax.set_title(group, fontsize=12)
        ax.set_xlabel(count_col, fontsize=10)
        ax.set_ylabel(keyword_col, fontsize=10)
        ax.tick_params(labelsize=10)

    for ax in axes.flat[i+1:]:
        ax.axis('off')

    plt.suptitle(f'Top {n_top} {keyword_col} by {group_col}', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.show()

def plot_top_keywords_by_category(df: pd.DataFrame, n_top: int = 5,
                                figsize: Tuple[int, int] = (15, 8),
                                title: str = 'Top Keywords by Category') -> None:
    '''Create faceted bar plot of top keywords in each category.'''
    top_keywords = (df.groupby(['Category', 'Keyword'])['Count']
                    .sum()
                    .reset_index()
                    .sort_values('Count', ascending=False)
                    .groupby('Category')
                    .head(n_top))
    
    g = sns.FacetGrid(top_keywords, col='Category',
                      col_wrap=3, height=4, aspect=1.5)
    g.map_dataframe(sns.barplot, x='Count', y='Keyword',
                    color='mediumseagreen')
    
    g.fig.suptitle(title, y=1.02)
    plt.tight_layout()
    plt.show()