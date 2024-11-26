import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

def detect_outliers(df: pd.DataFrame, numerical_cols: list[str]) -> tuple[dict, list]:
    '''Detect outliers using IQR method.'''
    outlier_info = {}  # dictionary to store index and source
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

def plot_boxplot(df: pd.DataFrame, numerical_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    ''' Plot numerical columns in a single boxplot using melted data + identify outliers. Returns outliers_df, original_rows_with_outliers.'''
    plt.figure(figsize=(5, 3))
    melted_df = df[numerical_cols].melt(var_name='Variable', value_name='EUR per month')
    ax = sns.boxplot(data=melted_df, x='Variable', y='EUR per month', width=0.2, 
                    color='mediumseagreen', 
                    showfliers=False)
    
    outlier_info, outliers_data = detect_outliers(df, numerical_cols)
    outliers_df = pd.DataFrame(outliers_data, columns=['Variable', 'EUR per month']) if outliers_data else pd.DataFrame()
    
    if not outliers_df.empty:
        sns.stripplot(data=outliers_df, x='Variable', y='EUR per month',
                     color='darkgreen', size=6, alpha=0.6,
                     jitter=0.2)
    
    plt.title('Min vs Max Salary')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Get the full rows from original DataFrame and add outlier source
    original_rows = df.loc[list(outlier_info.keys())].copy()
    original_rows['outlier_source'] = [','.join(sources) for sources in outlier_info.values()]
    
    return outliers_df, original_rows

def plot_common_keywords(common_keywords, country):
    '''
    Creates a bar chart to visualize the most common keywords found in job descriptions for a specific country.

    Args:
        common_keywords: A list of tuples where each tuple contains a keyword (string) and its frequency (integer).
        country: The name of the country to be displayed in the plot title.
    '''
    # Unzip the list of tuples into two lists: words and counts
    words, counts = zip(*common_keywords)
    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.bar(words, counts, color='mediumseagreen')  # Bar plot
    plt.xlabel('Keywords', fontsize=14)  # Label for x-axis
    plt.ylabel('Frequency', fontsize=14)  # Label for y-axis
    plt.title(f'Most Common Keywords in Job Descriptions - {country}', fontsize=16)  # Title of the plot
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to make room for rotated labels
    plt.show()  # Display the plot


def plot_grouped_histograms(df, group_col, value_col, bins=10, kde=True, figsize=(16, 6), title='Histogram'):
    '''Plots histograms for a numerical column grouped by a categorical column.'''
    unique_groups = df[group_col].unique()
    fig, axes = plt.subplots(1, len(unique_groups), figsize=figsize)

    for i, group in enumerate(unique_groups):
        group_data = df[df[group_col] == group]
        sns.histplot(
            x=value_col,
            data=group_data,
            bins=bins,
            kde=kde,
            alpha=0.5,
            color='mediumseagreen',
            ax=axes[i]
        )
        axes[i].set_title(group)
        axes[i].set_xlabel('EUR')
        axes[i].set_ylabel('Frequency')

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()



def plot_top_keywords_by_category(df, n_top=5, figsize=(15, 8), title="Top Keywords by Category"):
    '''
    Creates a faceted bar plot showing top keywords in each category.
    
    Args:
        df: DataFrame containing columns 'Category', 'Keyword', 'Count'
        n_top: Number of top keywords to show per category
        figsize: Tuple for figure size
        title: String for plot title
    '''
    # Get top n keywords per category
    top_keywords = (df.groupby(['Category', 'Keyword'])['Count']
                   .sum()
                   .reset_index()
                   .sort_values('Count', ascending=False)
                   .groupby('Category')
                   .head(n_top))
    
    # Create faceted bar plot
    g = sns.FacetGrid(
        top_keywords,
        col='Category',
        col_wrap=3,
        height=4,
        aspect=1.5
    )
    
    g.map_dataframe(
        sns.barplot,
        x='Count',
        y='Keyword',
        color='mediumseagreen'
    )
    
    # Customize the plot
    g.fig.suptitle(title, y=1.02)
    plt.tight_layout()
    plt.show()

##################

def plot_grouped_bar(df, group_col, value_col, figsize=(16, 8), title='Bar Plot', top_n=10):
  """
  Plots bar plots for a categorical column grouped by another categorical column.

  Args:
      df (DataFrame): The data source.
      group_col (str): The column to group by (e.g., country).
      value_col (str): The categorical column to count (e.g., job_title).
      figsize (tuple): Figure size - made taller by default.
      title (str): Overall title for the plot.
      top_n (int): Number of top categories to show.
  """

  unique_groups = df[group_col].unique()

  # Create figure with more bottom space
  fig, axes = plt.subplots(1, len(unique_groups), figsize=figsize)

  for i, group in enumerate(unique_groups):
    # Get data for this group
    group_data = df[df[group_col] == group]

    # Get top n categories for this group
    top_categories = group_data[value_col].value_counts().nlargest(top_n)

    # Create bar plot
    sns.countplot(
        data=group_data,
        x=value_col,
        order=top_categories.index,
        color='mediumseagreen',
        ax=axes[i],
        width=0.6  # Make bars thinner
    )

    axes[i].set_title(group)

    # Rotate labels at 45 degrees and align them
    for label in axes[i].get_xticklabels():
      label.set_rotation(45)
      label.set_ha('right')  # Align the labels to the right

    # Remove x-label as it's redundant
    axes[i].set_xlabel('')

  # Overall plot title
  plt.suptitle(title)

  # Adjust subplot parameters to give specified padding
  plt.subplots_adjust(bottom=0.2)  # Increase bottom margin

  plt.show()

def plot_skills_bars(df: pd.DataFrame, 
                   figsize: tuple[int, int] = (15, 8)) -> None:
   """Create a grouped bar chart of skills frequency by role, sorted by overall frequency."""
   plt.figure(figsize=figsize)
   
   # Sort skills by average frequency across roles
   skill_order = (df.groupby('Keyword')['Frequency']
                 .mean()
                 .sort_values(ascending=False)
                 .index)
   
   sns.barplot(data=df,
               x='Keyword',
               y='Frequency',
               hue='Search Keyword',
               palette='Set2',
               order=skill_order)  # Use sorted order
   
   plt.title('Required Skills Frequency by Role')
   plt.xlabel('Skill')
   plt.ylabel('Frequency (%)')
   plt.xticks(rotation=45, ha='right')
   plt.legend(title='Role', bbox_to_anchor=(1.05, 1))
   plt.grid(True, alpha=0.3)
   plt.tight_layout()
   plt.show()

def plot_categorical(df: pd.DataFrame, categorical_cols: list[str], top_n: int = 10, 
                    horizontal: bool = False, figsize: tuple[int, int] = (5, 3)) -> None:
    """Bar chart plotting for categorical columns."""
    for col in categorical_cols:
        # Plot data
        fig, ax = plt.subplots(figsize=figsize)
        top_cats = df[col].value_counts().nlargest(top_n)
        
        # Choose x or y based on orientation
        plot_kwargs = {'y': col} if horizontal else {'x': col}
        
        sns.countplot(
            data=df[df[col].isin(top_cats.index)],
            order=top_cats.index,
            color='mediumseagreen',
            ax=ax,
            **plot_kwargs
        )
        
        # Customize
        ax.set_title(f'Top {top_n} Categories of Column: {col}')
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        plt.show()

def plot_wordtree(
    data: list[str], 
    country: str,
    figsize: tuple[int, int] = (10, 5),
    width: int = 800,
    height: int = 400,
    background_color: str = 'white'
) -> None:
    """Creates and displays a word cloud visualization from a list of text descriptions."""
    text = ' '.join(data)
    
    wordcloud = WordCloud(
        width=width, 
        height=height, 
        background_color=background_color
    ).generate(text)
    
    plt.figure(figsize=figsize)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title(f'Wordcloud of Job Descriptions - {country}')
    plt.axis('off')
    plt.show()

def plot_stacked_bar_chart(df: pd.DataFrame,
                         title: str = "Stacked Bar Chart of Categories by Search Keyword",
                         colormap: str = 'inferno',
                         figsize: tuple[int, int] = (16, 10)) -> None:
   '''Creates a stacked bar chart showing category distribution by search keyword.'''
   
   # Create and plot stacked bars
   (df.pivot_table(index='Search Keyword', 
                  columns='Category', 
                  values='Count',
                  aggfunc='sum',
                  observed=True)
    .fillna(0)
    .plot(kind='bar', 
          stacked=True, 
          colormap=colormap,
          edgecolor='black',
          figsize=figsize))
   
   # Customize plot
   plt.title(title, fontsize=16, pad=20)
   plt.xlabel('Search Keyword', fontsize=14)
   plt.ylabel('Count', fontsize=14)
   plt.xticks(rotation=90, fontsize=12)
   plt.yticks(fontsize=12)
   plt.legend(title='Category', 
             bbox_to_anchor=(1.05, 1), 
             loc='upper left', 
             fontsize=12)
   
   plt.tight_layout()
   plt.show()


def plot_top_keyword_heatmap(df: pd.DataFrame, 
                         top_n: int = 15, 
                         figsize: tuple[int, int] = (15, 10),
                         title: str = "Top Keyword Distribution Across Job Titles") -> None:
   '''Creates a heatmap showing top N aggregated keywords across job titles.'''
   
   # Get top N keyword combinations
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
   
   # Plot heatmap
   plt.figure(figsize=figsize)
   sns.heatmap(top_combinations, annot=True, fmt='.0f', 
               cmap='YlOrRd', cbar_kws={'label': 'Count'})
   
   plt.title(title, pad=20)
   plt.xlabel('Skill', fontsize=12)
   plt.ylabel('Role', fontsize=12)
   plt.xticks(rotation=45)
   plt.tight_layout()
   plt.show()

def plot_keywords_per_group_subplots(df: pd.DataFrame, group_col: str, keyword_col: str, count_col: str, n_top: int = 5, 
                                         figsize: tuple[int, int] = (16, 12)) -> None:
    """Creates small subplots for each group in the specified column, showing its top N keywords.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        group_col (str): The column name to group the data by.
        keyword_col (str): The column name for the keywords.
        count_col (str): The column name for the counts.
        n_top (int, optional): The number of top keywords to display. Defaults to 5.
        figsize (tuple, optional): The figure size. Defaults to (16, 12).
    """

    groups = df[group_col].unique()
    n_cols = 3
    n_rows = -(-len(groups) // n_cols)  # ceil division

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)

    for i, (group, ax) in enumerate(zip(groups, axes.flatten())):
        # Filter and group data by the specified group
        group_data = df[df[group_col] == group]
        top_keywords = (group_data
                         .groupby(keyword_col)[count_col]
                         .sum()
                         .nlargest(n_top)
                         .reset_index())

        sns.barplot(data=top_keywords, x=count_col, y=keyword_col, color='mediumseagreen', ax=ax)

        ax.set_title(group, fontsize=12)
        ax.set_xlabel(count_col, fontsize=10)
        ax.set_ylabel(keyword_col, fontsize=10)
        ax.tick_params(labelsize=10)

    # Hide unused axes
    for ax in axes.flat[i+1:]:
        ax.axis('off')

    plt.suptitle(f"Top {n_top} {keyword_col} by {group_col}", fontsize=16, y=1.02)
    plt.tight_layout()
    plt.show()
