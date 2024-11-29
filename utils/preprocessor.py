import pandas as pd

from utils.dictionaries import LOCATION_MAPPINGS, CLEANING_PATTERNS

def merge_US_cities(cities: list[str], DATA_PATH: str) -> pd.DataFrame:
    # Load data for the first city and add the 'country' column manually
    df_NY = pd.read_csv(f'{DATA_PATH}{"USA_"}{cities[0]}.csv')
    df_NY['country'] = 'USA' # Add the 'country' column to match format
    print(f'Loaded data for {cities[0]}')

    # Load data for other cities
    df_LA = pd.read_csv(f'{DATA_PATH}{"USA_"}{cities[1]}.csv')
    df_CHI = pd.read_csv(f'{DATA_PATH}{"USA_"}{cities[2]}.csv')

    # Ensure consistent column order across DataFrames
    desired_order = df_LA.columns.tolist()
    df_NY = df_NY[desired_order]
    print(f'Column order for consistency: {desired_order}')

    # Concatenate the DataFrames
    df_USA = pd.concat([df_NY, df_LA, df_CHI], ignore_index=True)

    # Verify column order consistency 
    assert df_USA.columns.tolist() == desired_order, 'Column order mismatch!'

    return df_USA

def check_duplicates(data: pd.DataFrame) -> None:
    num_rows = len(data)
    duplicates = data[data.duplicated()]
    num_duplicates = len(duplicates)
    print(f'DataFrame with {num_rows} rows has {num_duplicates} duplicates.')
    if num_duplicates > 0:
        print(duplicates)

def remove_duplicates_jobdesc(data: pd.DataFrame) -> pd.DataFrame:
   '''Remove duplicates based on the core identifying information of the job posting.'''
   # Get country name if it exists in the data
   country_name = data['country'].iloc[0] if 'country' in data.columns else 'Unknown'
   
   # Use columns that identify unique job postings
   subset1 = [
       'company_name',
       'company_location',
       'job_description_norm', # normalized description to catch true duplicates
       'salary'
   ]
   
   output1 = data.drop_duplicates(subset=subset1, keep='last')
   
   # Then remove cross-listed duplicates using job_link as backup
   output2 = output1.drop_duplicates(subset=['job_link'], keep='last')
   
   # Show duplicates that were removed
   if len(data) > len(output2):
       print(f"Initial rows: {len(data)}")
       print(f"Rows after removing exact duplicates: {len(output1)}")
       print(f"Final rows: {len(output2)}")
       print(f"Total duplicates removed: {len(data) - len(output2)}")
       #print("-" * 50)
       
   return output2


def standardize_locations_2(df: pd.DataFrame,
                       location_column: str,
                       department_mapping: dict[str, str],
                       region_mapping: dict[str, str],
                       country: str,
                       cleaning_patterns: dict = CLEANING_PATTERNS) -> pd.DataFrame:
    df = df.copy()
    df['location_clean'] = df[location_column].str.lower()
    
    # Apply cleaning patterns
    for pattern, replacement in cleaning_patterns.get(country, []):
        df['location_clean'] = df['location_clean'].str.replace(pattern, replacement, regex=True)
    
    df['location_clean'] = df['location_clean'].str.strip()
    
    # Special handling for each country
    if country == 'France':
        case_insensitive_mapping = {k.lower(): v for k, v in department_mapping.items()}
        df['department'] = df['location_clean'].map(case_insensitive_mapping)
        df['location_clean'] = df['location_clean'].apply(lambda x: 
            '-'.join(word.capitalize() if i == 0 or word.lower() not in 
                    ['sur', 'en', 'le', 'la', 'les', 'sous', 'aux', 'de', 'du', 'des', 'd', 'l'] 
                    else word.lower() 
                    for i, word in enumerate(x.split('-'))))
    elif country == 'USA':
        df['state_code'] = df[location_column].str.extract(r',?\s*([A-Z]{2})\s*(?:\d{5})?')[0]
        df['location_clean'] = df['location_clean'].str.title()
        df['department'] = df.apply(
            lambda row: department_mapping.get(row['location_clean']) or 
            "NY - New York State" if row['location_clean'] in 
            ['New York', 'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
            else f"{row['state_code']} - {row['state_code']} State",
            axis=1)
        df['dept_number'] = df['state_code']
    else:
        df['location_clean'] = df['location_clean'].str.title()
        df['department'] = df['location_clean'].map(department_mapping)
        df['dept_number'] = df['department'].str.extract(r'^(\w{2})')
    
    if country != 'USA':
        df['dept_number'] = df['department'].str.extract(r'^(\w{2})')
    
    df['region'] = df['dept_number'].map(region_mapping)
    df['city_name'] = df['location_clean']
    df['country'] = country
    
    return df[['job_id', location_column, 'city_name', 'department', 'region', 'country']]

def standardize_locations(df: pd.DataFrame, 
                       location_column: str, 
                       department_mapping: dict[str, str], 
                       region_mapping: dict[str, str],
                       country: str) -> pd.DataFrame:
    df = df.copy()
    
    if country == 'France':
        df.loc[:, 'location_clean'] = df[location_column].str.lower()
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'télétravail\s*(?:partiel|à)?\s*(?:à|en)?\s*', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\b\d{5}\b', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\(\d{2,3}\)', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\s\d{1,2}(?:er|ème|e)\s*', ' ', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.strip()
        # Create case-insensitive mapping dictionary for France
        case_insensitive_mapping = {k.lower(): v for k, v in department_mapping.items()}
        # Map using lowercase location names
        df.loc[:, 'department'] = df['location_clean'].str.lower().map(case_insensitive_mapping)
        # After mapping, capitalize for display
        df.loc[:, 'location_clean'] = df['location_clean'].apply(lambda x: 
            '-'.join(word.capitalize() if i == 0 or not word.lower() in ['sur', 'en', 'le', 'la', 'les', 'sous', 'aux', 'de', 'du', 'des', 'd', 'l'] 
                    else word.lower() 
                    for i, word in enumerate(x.split('-'))))
      
    elif country == 'Sweden':
        df.loc[:, 'location_clean'] = df[location_column].str.lower()
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'distansjobb\s+(?:i|in)\s+', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\d{3}\s?\d{2}\s?', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.strip()
        df.loc[:, 'location_clean'] = df['location_clean'].str.title()
        # Map locations to departments
        df.loc[:, 'department'] = df['location_clean'].map(department_mapping)
    
    elif country == 'Italy':
        df.loc[:, 'location_clean'] = df[location_column].str.lower()
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'remoto\s+(?:in|a)\s+', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'parzialmente\s+remoto\s+in\s+', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\d{5}\s?', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r',\s*\w+', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'provincia\s+di\s+', '', regex=True)
        df.loc[:, 'location_clean'] = df['location_clean'].str.strip()
        df.loc[:, 'location_clean'] = df['location_clean'].str.title()
        # Map locations to departments
        df.loc[:, 'department'] = df['location_clean'].map(department_mapping)
        
    elif country == 'USA':
        df.loc[:, 'location_clean'] = df[location_column].str.lower()
        # Extract state code before cleaning
        df['state_code'] = df[location_column].str.extract(r',?\s*([A-Z]{2})\s*(?:\d{5})?')[0]
        # Remove hybrid/remote work mentions
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'hybrid\s+work\s+in\s+|remote\s+in\s+', '', regex=True)
        # Remove zip codes
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\s+\d{5}(?:-\d{4})?', '', regex=True)
        # Extract city name (everything before the state)
        df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r',?\s*[a-z]{2}(?:\s+\d{5}(?:-\d{4})?)?$', '', regex=True)
        # Clean up any remaining whitespace and capitalize
        df.loc[:, 'location_clean'] = df['location_clean'].str.strip().str.title()
        # Map to department using both city and state
        df.loc[:, 'department'] = df.apply(
            lambda row: department_mapping.get(row['location_clean']) or "NY - New York State" 
            if row['location_clean'] in ['New York', 'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
            else department_mapping.get(row['location_clean']) or f"{row['state_code']} - {row['state_code']} State",
            axis=1
        )
        # Set department number to state code for USA
        df.loc[:, 'dept_number'] = df['state_code']
    
    # Extract department number for non-USA countries
    if country != 'USA':
        df.loc[:, 'dept_number'] = df['department'].str.extract(r'^(\w{2})')
    
    # Map to region for all countries
    df.loc[:, 'region'] = df['dept_number'].map(region_mapping)
    df.loc[:, 'city_name'] = df['location_clean']
    df.loc[:, 'country'] = country
    
    return df[['job_id', location_column, 'city_name', 'department', 'region', 'country']]
