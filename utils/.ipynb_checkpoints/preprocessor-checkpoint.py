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
    subset = ['job_description', 'search_location', 'job_title']
    output = data.drop_duplicates(subset=subset, keep='last')
    print(f'Removed {len(data) - len(output)} duplicates based on {subset}. Size before: {len(data)}. Size after: {len(output)}')
    return output