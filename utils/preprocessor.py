import pandas as pd

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
       print("-" * 50)
       
   return output2

def standardize_locations(df: pd.DataFrame, 
                        location_column: str, 
                        department_mapping: dict[str, str], 
                        region_mapping: dict[str, str]) -> pd.DataFrame:
    df = df.copy()
    
    df.loc[:, 'location_clean'] = df[location_column].str.replace(r'Télétravail (?:partiel |à )?à ?', '', regex=True)
    df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\d{5}\s?', '', regex=True)
    df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\(\d{2}\)', '', regex=True)
    df.loc[:, 'location_clean'] = df['location_clean'].str.replace(r'\s\d{1,2}e', '', regex=True)
    df.loc[:, 'location_clean'] = df['location_clean'].str.strip()
    
    df.loc[:, 'department'] = df['location_clean'].map(department_mapping)
    df.loc[:, 'dept_number'] = df['department'].str.extract(r'(\d{2})')
    df.loc[:, 'region'] = df['dept_number'].map(region_mapping)
    
    df.loc[:, 'postal_code'] = df[location_column].str.extract(r'(\d{5})')
    df.loc[:, 'city_name'] = df['location_clean']
    df.loc[:, 'country'] = 'France'
    
    return df[['job_id', location_column, 'city_name', 'department', 'region', 'country', 'postal_code']]