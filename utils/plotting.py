import matplotlib.pyplot as plt
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


def plot_keyword_heatmap(df, figsize=(15, 10), title="Keyword Distribution Across Countries and Job Titles"):
    """
    Creates a heatmap showing the distribution of keywords across countries and job titles.
    
    Args:
        df: DataFrame containing columns 'Category', 'Keyword', 'Search Keyword', 'Country', 'Count'
        figsize: Tuple for figure size
        title: String for plot title
    """
    # Create pivot table for the heatmap
    pivot_data = df.pivot_table(
        values='Count',
        index=['Category', 'Keyword'],  # Multi-level index
        columns=['Country', 'Search Keyword'],
        fill_value=0
    )
    
    # Create figure with appropriate size
    plt.figure(figsize=figsize)
    
    # Create heatmap
    sns.heatmap(
        pivot_data,
        cmap='YlGn',  # Yellow to Green colormap
        annot=True,    # Show numbers in cells
        fmt='g',       # Format as general number
        cbar_kws={'label': 'Count'},
        square=True,   # Make cells square
    )
    
    # Customize the plot
    plt.title(title, pad=20)
    
    # Rotate labels if needed
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
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