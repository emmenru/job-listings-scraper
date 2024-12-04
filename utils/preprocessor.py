import re
from typing import List

import pandas as pd

from utils.dictionaries import LOCATION_MAPPINGS, CLEANING_PATTERNS


def merge_US_cities(cities: List[str], DATA_PATH: str) -> pd.DataFrame:
    '''Merge data from multiple US cities into single DataFrame.'''
    df_NY = pd.read_csv(f'{DATA_PATH}USA_{cities[0]}.csv')
    df_NY['country'] = 'USA'
    print(f'Loaded data for {cities[0]}')

    df_LA = pd.read_csv(f'{DATA_PATH}USA_{cities[1]}.csv')
    df_CHI = pd.read_csv(f'{DATA_PATH}USA_{cities[2]}.csv')

    desired_order = df_LA.columns.tolist()
    df_NY = df_NY[desired_order]
    print(f'Column order for consistency: {desired_order}')

    df_USA = pd.concat([df_NY, df_LA, df_CHI], ignore_index=True)

    assert df_USA.columns.tolist() == desired_order, 'Column order mismatch!'
    return df_USA


def check_duplicates(data: pd.DataFrame) -> None:
    '''Print number and details of duplicate rows.'''
    num_rows = len(data)
    duplicates = data[data.duplicated()]
    num_duplicates = len(duplicates)
    print(f'DataFrame with {num_rows} rows has {num_duplicates} duplicates.')
    if num_duplicates > 0:
        print(duplicates)


def remove_duplicates_jobdesc(data: pd.DataFrame) -> pd.DataFrame:
    '''Remove duplicates based on core job posting information.'''
    country_name = data['country'].iloc[0] if 'country' in data.columns else 'Unknown'
   
    subset1 = [
        'company_name',
        'company_location',
        'job_description_norm',
        'salary'
    ]
   
    output1 = data.drop_duplicates(subset=subset1, keep='last')
    output2 = output1.drop_duplicates(subset=['job_link'], keep='last')
   
    if len(data) > len(output2):
        print(f'Initial rows: {len(data)}')
        print(f'Rows after removing exact duplicates: {len(output1)}')
        print(f'Final rows: {len(output2)}')
        print(f'Total duplicates removed: {len(data) - len(output2)}')
       
    return output2


def standardize_locations(df: pd.DataFrame,
                         location_column: str,
                         country: str) -> pd.DataFrame:
    '''Standardize location data based on country-specific mappings.'''
    dept_mapping = LOCATION_MAPPINGS[country]['departments']
    region_mapping = LOCATION_MAPPINGS[country]['regions']    
    df = df.copy()
    df['location_clean'] = df[location_column].str.lower()
    
    for pattern, replacement in CLEANING_PATTERNS.get(country, []):
        df['location_clean'] = df['location_clean'].str.replace(pattern, replacement, regex=True)
    
    df['location_clean'] = df['location_clean'].str.strip()
    
    if country == 'France':
        case_insensitive_mapping = {k.lower(): v for k, v in dept_mapping.items()}
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
            lambda row: dept_mapping.get(row['location_clean']) or 
            'NY - New York State' if row['location_clean'] in 
            ['New York', 'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
            else f"{row['state_code']} - {row['state_code']} State",
            axis=1)
        df['dept_number'] = df['state_code']
    else:
        df['location_clean'] = df['location_clean'].str.title()
        df['department'] = df['location_clean'].map(dept_mapping)
        df['dept_number'] = df['department'].str.extract(r'^(\w{2})')
    
    if country != 'USA':
        df['dept_number'] = df['department'].str.extract(r'^(\w{2})')
    
    df['region'] = df['dept_number'].map(region_mapping)
    df['city_name'] = df['location_clean']
    df['country'] = country
    
    return df[['job_id', location_column, 'city_name', 'department', 'region', 'country']]