import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

def plot_categorical(df, categorical_cols, top_n=10, horizontal=False, figsize=(10, 6)):
    """
    Creates bar charts to visualize the distribution of categorical columns in a DataFrame.
    Args:
        df: The DataFrame containing the data.
        categorical_cols: A list of strings representing the categorical columns to plot.
        top_n: An integer specifying the number of top categories to display (default: 10).
        horizontal: A boolean indicating whether to create a horizontal bar chart (default: False).
        figsize: Tuple specifying the figure size (width, height) for each plot.
    """
    for col in categorical_cols:
        plt.figure(figsize=figsize)
        
        # Count the top categories
        top_categories = df[col].value_counts().nlargest(top_n)
        
        # Create a count plot with mediumseagreen color
        if horizontal:
            sns.countplot(data=df, y=col, order=top_categories.index, color='mediumseagreen')
        else:
            sns.countplot(data=df, x=col, order=top_categories.index, color='mediumseagreen')
        
        plt.title(f'Top {top_n} Categories of Column: {col}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def plot_numerical(df, numerical_cols):
    """
    Performs exploratory data analysis for specified numerical columns in a DataFrame and generates visualizations.

    Args:
        df: The DataFrame containing the data.
        numerical_cols: A list of strings representing the numerical columns to analyze.
    """
    for col in numerical_cols:
        # Drop NaN values and check for valid data
        valid_data = df[col].dropna()
        
        # Check if there are enough values to plot
        # Summary statistics
        print(f"Summary statistics for {col}:")
        print(valid_data.describe())
        print("\n")
            
        # Boxplot
        plt.figure(figsize=(12, 6))
        sns.boxplot(x=valid_data)  # Use valid data for plotting
        plt.title(f'Boxplot of Column {col}')
        plt.xlabel(col)
        plt.grid()
        plt.show()

def plot_common_keywords(common_keywords, country):
    """
    Creates a bar chart to visualize the most common keywords found in job descriptions for a specific country.

    Args:
        common_keywords: A list of tuples where each tuple contains a keyword (string) and its frequency (integer).
        country: The name of the country to be displayed in the plot title.
    """
    # Unzip the list of tuples into two lists: words and counts
    words, counts = zip(*common_keywords)

    # Create a bar plot
    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.bar(words, counts, color='mediumseagreen')  # Bar plot
    plt.xlabel('Keywords', fontsize=14)  # Label for x-axis
    plt.ylabel('Frequency', fontsize=14)  # Label for y-axis
    plt.title(f'Most Common Keywords in Job Descriptions - {country}', fontsize=16)  # Title of the plot
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to make room for rotated labels
    plt.show()  # Display the plot

def plot_wordtree(data, country):
    # Combine all the text into a single string 
    text = ' '.join(data)
    # Create a wordcloud object
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    # Display the wordcloud 
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title(f'Wordcloud of Job Descriptions - {country}')
    plt.axis('off')
    plt.show()
import matplotlib.pyplot as plt

def plot_stacked_bar_chart(df, title="Stacked Bar Chart of Categories by Search Keyword", colormap='inferno', figsize=(16, 10)):
    """
    Creates a stacked bar chart showing the distribution of categories by search keyword.
    
    Args:
        df: DataFrame containing 'Search Keyword', 'Category', and 'Count' columns
        title: Title of the plot
        colormap: Colormap for the stacked bars
        figsize: Tuple for figure size
    """
    # Pivot the data for the stacked bar chart
    pivot_df = df.pivot_table(
        index='Search Keyword', 
        columns='Category', 
        values='Count', 
        aggfunc='sum', 
        observed=True
    ).fillna(0)

    # Create the figure and plot the stacked bar chart
    plt.figure(figsize=figsize)
    pivot_df.plot(kind='bar', stacked=True, colormap=colormap, edgecolor='black', figsize=figsize)

    # Customize the plot
    plt.title(title, fontsize=16)
    plt.xlabel('Search Keyword', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.xticks(rotation=90, fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
    plt.tight_layout()

    # Show the plot
    plt.show()


def plot_grouped_histograms(df, group_col, value_col, bins=10, kde=True, figsize=(16, 6), title='Histogram'):
    """
    Plots histograms for a numerical column grouped by a categorical column.

    Args:
        df (DataFrame): The data source.
        group_col (str): The column to group by (e.g., country).
        value_col (str): The numerical column to plot (e.g., salary).
        bins (int): Number of bins for the histogram.
        kde (bool): Whether to include a Kernel Density Estimate (KDE) curve.
        figsize (tuple): Figure size.
        title (str): Overall title for the plot.
    """
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

def plot_grouped_boxplots(df, group_col, value_col, figsize=(16, 6), title='Boxplot'):
    """
    Plots boxplots for a numerical column grouped by a categorical column.
    Args:
        df (DataFrame): The data source.
        group_col (str): The column to group by (e.g., country).
        value_col (str): The numerical column to plot (e.g., salary).
        figsize (tuple): Figure size.
        title (str): Overall title for the plot.
    """
    unique_groups = df[group_col].unique()
    fig, axes = plt.subplots(1, len(unique_groups), figsize=figsize)
    
    for i, group in enumerate(unique_groups):
        group_data = df[df[group_col] == group]
        sns.boxplot(
            y=value_col,
            data=group_data,
            color='mediumseagreen',
            ax=axes[i]
        )
        axes[i].set_title(group)
        axes[i].set_ylabel('EUR')
    
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()
    
def plot_grouped_barplots(df, group_col, value_col, figsize=(16, 8), title='Bar Plot', top_n=10):
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
        ax = sns.countplot(
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
        
        axes[i].set_xlabel('')  # Remove x-label as it's redundant
    
    plt.suptitle(title)
    
    # Adjust the subplot parameters to give specified padding
    plt.subplots_adjust(bottom=0.2)  # Increase bottom margin
    
    plt.show()

def plot_top_keyword_heatmap(df, top_n=15, figsize=(15, 10), title="Top Keyword Distribution Across Job Titles"):
    """
    Creates a simplified heatmap showing the top N aggregated keywords across job titles.

    Args:
        df: DataFrame containing columns 'Category', 'Keyword', 'Search Keyword', 'Count'
        top_n: Integer for the number of top combinations to include
        figsize: Tuple for figure size
        title: String for plot title
    """
    # Aggregate data across all countries
    aggregated_data = df.groupby(
        ['Category', 'Keyword', 'Search Keyword'], 
        as_index=False, 
        observed=True  # Using observed=True to handle categories correctly
    )['Count'].sum()

    # Filter to keep only the top N combinations based on their total Count
    top_combinations = (
        aggregated_data.groupby(['Category', 'Keyword'])['Count']
        .sum()
        .nlargest(top_n)
        .reset_index()[['Category', 'Keyword']]
    )

    # Merge to retain only rows matching the top combinations
    filtered_data = aggregated_data.merge(top_combinations, on=['Category', 'Keyword'])

    # Create pivot table for the heatmap
    heatmap_data = filtered_data.pivot(
        index='Search Keyword', 
        columns='Keyword', 
        values='Count'
    )

    # Create figure with appropriate size
    plt.figure(figsize=figsize)

    # Create heatmap
    sns.heatmap(
        heatmap_data, 
        annot=True, fmt='.0f', cmap='YlOrRd', 
        cbar_kws={'label': 'Count'}
    )

    # Customize the plot
    plt.title(title)
    plt.xlabel('Skill')
    plt.ylabel('Role')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show plot
    plt.show()


def plot_top_keywords_by_category(df, n_top=5, figsize=(15, 8), title="Top Keywords by Category"):
    """
    Creates a faceted bar plot showing top keywords in each category.
    
    Args:
        df: DataFrame containing columns 'Category', 'Keyword', 'Count'
        n_top: Number of top keywords to show per category
        figsize: Tuple for figure size
        title: String for plot title
    """
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
    
def plot_keywords_per_category_subplots(df, n_top=5, figsize=(16, 12)):
    """
    Creates small subplots for each Category showing its top N keywords.

    Args:
        df: DataFrame containing columns 'Category', 'Keyword', 'Count'.
        n_top: Number of top keywords to display per category.
        figsize: Tuple for the overall figure size.
    """
    # Get the unique categories
    categories = df['Category'].unique()

    # Create a grid of subplots
    n_categories = len(categories)
    n_cols = 3  # Number of columns
    n_rows = -(-n_categories // n_cols)  # Calculate rows needed (ceil division)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, constrained_layout=True)
    axes = axes.flatten()  # Flatten the axes array for easy iteration

    for i, category in enumerate(categories):
        # Filter the data for the current category
        category_data = df[df['Category'] == category]

        # Get top n keywords for the current category
        top_keywords = (category_data.groupby('Keyword')['Count']
                        .sum()
                        .nlargest(n_top)
                        .reset_index())

        # Plot the data
        sns.barplot(
            data=top_keywords,
            x='Count',
            y='Keyword',
            color='mediumseagreen',
            ax=axes[i]
        )

        # Customize each subplot
        axes[i].set_title(f"{category}", fontsize=10)
        axes[i].set_xlabel('Count', fontsize=8)
        axes[i].set_ylabel('Keyword', fontsize=8)
        axes[i].tick_params(axis='both', labelsize=8)

    # Hide any unused axes
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    # Add a main title for the figure
    fig.suptitle(f"Top {n_top} Keywords by Category", fontsize=16, y=1.02)

    # Show the figure
    plt.tight_layout()
    plt.show()

