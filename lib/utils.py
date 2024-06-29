import pandas as pd
import copy
import matplotlib.pyplot as plt


def check_file_name(expected_file_name: str, input_file_name: str):
    if expected_file_name != input_file_name:
        raise ValueError(f'Expected {expected_file_name}. Got {input_file_name}')



def check_ticker_values(dataframe: pd.DataFrame):
    unique_ticker_names = list(dataframe['ticker'].unique())
    uncorrect_ticker_names = [ticker_name for ticker_name in unique_ticker_names if len(ticker_name) != 3]
    if uncorrect_ticker_names != []:
        raise ValueError(f'Expected 3 letter-capital-named tickers. Got {uncorrect_ticker_names}') 



def check_column_type(dataframe: pd.DataFrame, column: str, expected_type: str):
    input_type = dataframe[column].dtype 
    if input_type != expected_type:
        raise TypeError(f'{column} type is {expected_type}. Got {input_type}')



def check_negative_values(dataframe: pd.DataFrame, column: str):
    if (dataframe[column]<0).any():
        raise ValueError(f'Values in {column} should be greater or equal to 0')

    

def is_dataframe_empty(dataframe: pd.DataFrame, function: callable):
    if dataframe.empty:
        raise ValueError(f'Dataframe is empty. Make sure you ran {function.__name__}')



def evolution(df: pd.DataFrame, start: int, end: int, unit: str, save_path: str = None):

    """
    start: date. If year: YYYY; if year_month: YYYYMM
    end: date. If year: YYYY; if year_month: YYYYMM 
    unit: USD or pct
    """

    # Dates must be 4-or-6 sized and their lengths must be equal (e.g: if start = 2024, end cannot be 202406)
    start_length = len(str(start))
    end_length = len(str(end))
    valid_length = [4,6]
    if (start_length not in valid_length or end_length not in valid_length) or (start_length != end_length):
        raise ValueError('start and end parameters must be 4 or 6 characters long and have same length')
    
    # The end date cannot be inferior or equal to the start date 
    if end<start:
        raise ValueError('end argument must be greater than start')
    
    # Performance only available in USD or %
    if unit != 'USD' and unit != 'pct':
        raise ValueError('unit parameter must be either "USD" or "pct"')


    # Initialize a figure with given size 
    plt.figure(figsize=(12,6))


    if start_length == 6:

        # Check if input dataframe is correct
        if 'year_month' not in df.columns or ('portfolio_monthly_performance_USD' not in df.columns and 'portfolio_monthly_performance_pct' not in df.columns):
            raise ValueError('To get portfolio monthly evolution, dataframe should at least contain "year_month" and "portfolio_monthly_performance_USD"/"portfolio_monthly_performance_pct" attributes')

        # Even if they have correct lengths, check if start and end dates are valid dates
        unique_dates = df['year_month'].unique()  
        if start not in unique_dates or end not in unique_dates:
            raise ValueError('Invalid dates')

        df_sliced = copy.deepcopy(df[(df['year_month']>=start) & (df['year_month']<=end)])
        df_sliced['year_month'] = pd.to_datetime(df_sliced['year_month'], format='%Y%m')

        plt.plot(df_sliced['year_month'], df_sliced[f'portfolio_monthly_performance_{unit}'], label={unit})


    elif start_length == 4:

        # Check if input dataframe is correct
        if 'year' not in df.columns or ('portfolio_yearly_performance_USD' not in df.columns and 'portfolio_yearly_performance_pct' not in df.columns):
            raise ValueError('To get portfolio yearly evolution, dataframe should at least contain "year" and "portfolio_yearly_performance_USD"/"portfolio_yearly_performance_pct" attributes')

        # Even if they have correct lengths, check if start and end dates are valid dates
        unique_dates = df['year'].unique()  
        if start not in unique_dates or end not in unique_dates:
            raise ValueError('Invalid dates')

        df_sliced = copy.deepcopy(df[(df['year']>=start) & (df['year']<=end)])
        df_sliced['year'] = pd.to_datetime(df_sliced['year'], format='%Y')

        plt.plot(df_sliced['year'], df_sliced[f'portfolio_yearly_performance_{unit}'], label={unit})
    

    plt.xlabel('Year')
    plt.ylabel('Performance')
    plt.title(f'Portfolio performance from {start} to {end} in {unit}')
    plt.legend()
    
    #plt.show()
    if save_path != None:
        plt.savefig(save_path)
        print(f'Portfolio evolution from {start} to {end} saved in {save_path}')



def composition(df: pd.DataFrame, date: int, save_path: str = None):

    """
    start: date. If year: YYYY; if year_month: YYYYMM
    end: date. If year: YYYY; if year_month: YYYYMM 
    """
    
    date_length = len(str(date))

    if date_length != 4 and date_length != 6:
        raise ValueError(f'Date must have 4 or 6 characters')    
    

    # Initialize a figure with given size 
    plt.figure(figsize=(8, 8))


    if date_length == 6:

        # Check if input dataframe is correct
        if 'year_month' not in df.columns or 'ticker' not in df.columns or 'ticker_monthly_value' not in df.columns:
            raise ValueError('To get portfolio monthly composition, dataframe should at least contain "year_month", "ticker" and "ticker_monthly_value"')  

        # Even if it has correct length, check if date is a valid date
        unique_dates = df['year_month'].unique()  
        if date not in unique_dates:
            raise ValueError('Invalid dates')

        df_sliced = copy.deepcopy(df[df['year_month']==date])
        df_sliced['year_month'] = pd.to_datetime(df_sliced['year_month'], format='%Y%m')

        plt.pie(df_sliced['ticker_monthly_value'], labels=df_sliced['ticker'], autopct='%1.1f%%', startangle=140)


    elif date_length == 4:

        # Check if input dataframe is correct
        if 'year' not in df.columns or 'ticker' not in df.columns or 'ticker_yearly_value' not in df.columns:
            raise ValueError('To get portfolio yearly composition, dataframe should at least contain "year", "ticker" and "ticker_yearly_value"')  

        # Even if it has correct length, check if date is a valid date
        unique_dates = df['year'].unique()  
        if date not in unique_dates:
            raise ValueError('Invalid dates')

        df_sliced = copy.deepcopy(df[(df['year']==date)])
        df_sliced['year'] = pd.to_datetime(df_sliced['year'], format='%Y')

        plt.pie(df_sliced['ticker_yearly_value'], labels=df_sliced['ticker'], autopct='%1.1f%%', startangle=140)
        

    plt.title(f'Portfolio composition in {date}')
    plt.legend()
    #plt.show()

    if save_path != None:
        plt.savefig(save_path)
        print(f'Portfolio composition in {date} saved in {save_path}')