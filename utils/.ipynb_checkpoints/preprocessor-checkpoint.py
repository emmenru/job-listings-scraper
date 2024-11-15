import pandas as pd

def merge_US_cities(cities, DATA_PATH):
    """
    Args:
        cities: A list of US city names, abbreviated.
        DATA_PATH: The base path to the CSV files containing job listings.

    Returns:
        A DataFrame containing the merged job listings from the specified cities.

    Raises:
        ValueError: If the provided `cities` list is empty.
        FileNotFoundError: If any of the specified CSV files are not found.

    Note:
        The function assumes that the CSV files have a consistent structure, including column names and data types.

    """
    
    # Load data for the first city and add the 'country' column manually
    df_NY = pd.read_csv(f"{DATA_PATH}{'USA_'}{cities[0]}.csv")
    df_NY['country'] = 'USA'  # Add the 'country' column to match format
    print("Loaded data for", cities[0])

    # Load data for other cities
    df_LA = pd.read_csv(f"{DATA_PATH}{'USA_'}{cities[1]}.csv")
    df_CHI = pd.read_csv(f"{DATA_PATH}{'USA_'}{cities[2]}.csv")

    # Ensure consistent column order across DataFrames
    desired_order = df_LA.columns.tolist()
    df_NY = df_NY[desired_order]
    print("Column order for consistency:", desired_order)

    # Concatenate the DataFrames
    df_USA = pd.concat([df_NY, df_LA, df_CHI], ignore_index=True)

    # Verify column order consistency 
    assert df_USA.columns.tolist() == desired_order, "Column order mismatch!"

    return df_USA

def check_duplicates(data):
    """
    # Note: The number of rows should be equal to the number of unique job links, etc 
    """
    # Get the number of rows 
    num_rows = data.shape[0]
    # Print the number of rows
    print(f'The DataFrame has {num_rows} rows.')
    print(data.nunique()) 
    # Check for duplicates in all columns
    duplicates = data.duplicated(keep=False)
    # Print duplicate rows 
    print(data[duplicates])

def remove_duplicates_jobdesc(data):
    """
    Checks for duplicatse (same job description, location, and job title) in the DataFrame and keeps only the latest entry if a duplicate is identified. 

    Args:
        data: The input DataFrame containing job listings.

    Returns:
        A DataFrame with duplicate job listings removed. The latest occurrence of a duplicate is retained.

    Raises:
        ValueError: If the input DataFrame is empty or missing required columns.

    Note:
        This function identifies and removes duplicate job listings based on the specified columns. If multiple duplicates exist for a specific job, only the latest occurrence is kept.
    """
    # Check if there are any duplicates based on 'job_description', 'location', and 'job_title'
    has_duplicates = data.duplicated(subset=['job_description', 'search_location', 'job_title'], keep=False).any()
    output = pd.DataFrame()
    
    if has_duplicates:
        print("There are duplicate values based on 'job_description', 'search_location', and 'job_title' columns.")
        
        # Below code is only if you want to inspect the duplicated entries  
        # Filter to include only rows with duplicates based on all three columns and sort by 'job_description'
        #output = data[data.duplicated(subset=['job_description', 'search_location', 'job_title'], keep=False)]
        #output = output.sort_values(by=['job_description', 'search_location', 'job_title']).reset_index(drop=True)
        # Display the duplicates
        #print(output)
        
        # Remove duplicates and keep only the last occurrence
        output = data.drop_duplicates(subset=['job_description', 'search_location', 'job_title'], keep='last').reset_index(drop=True)
    else:
        print("No duplicates found based on 'job_description', 'search_location', and 'job_title'.")
        output = data 
    print(f'Size before: {data.size}. Size after removing duplicates: {output.size} \n')
    return output

def desc_categorical(data):
    """
    Function for describing categorical data. 
    Prints value counts for categorical columns in the given DataFrame.
    Identifies string and object columns, excluding 'job_description' and 'job_link' columns. 
    """
    # Exclude these 
    string_columns = data.select_dtypes(include='string').drop(columns='job_description') # Skip job description! 
    object_columns = data.select_dtypes(include='object').drop(columns='job_link')

    # Loop through the columns and print value counts
    for col in string_columns.columns:
        print(f"Value counts for column: {col}\n{string_columns[col].value_counts()}\n")
    for col in object_columns.columns:
        print(f"Value counts for column: {col}\n{object_columns[col].value_counts()}\n")
