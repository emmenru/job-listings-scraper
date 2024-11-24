import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

def plot_categorical(df, categorical_cols, top_n=10, horizontal=False):
    """
    Creates bar charts to visualize the distribution of categorical columns in a DataFrame.

    Args:
        df: The DataFrame containing the data.
        categorical_cols: A list of strings representing the categorical columns to plot.
        top_n: An integer specifying the number of top categories to display (default: 10).
        horizontal: A boolean indicating whether to create a horizontal bar chart (default: False).
    """
    for col in categorical_cols:
        plt.figure(figsize=(10, 6))
        
        # Count the top categories
        top_categories = df[col].value_counts().nlargest(top_n)
        
        # Create a count plot
        if horizontal:
            sns.countplot(data=df, y=col, order=top_categories.index)
        else:
            sns.countplot(data=df, x=col, order=top_categories.index)
        
        plt.title(f'Top {top_n} Categories of Column: {col}')
        
        plt.xticks(rotation=45)
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
            ax=axes[i]
        )
        axes[i].set_title(group)
        axes[i].set_xlabel('EUR')
        axes[i].set_ylabel('Frequency')

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

