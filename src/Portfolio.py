import pandas as pd
import copy
from src.Transaction import Transaction
from src.Price import Price
from lib.utils import is_dataframe_empty



class Portfolio:



    def __init__(self, transaction: Transaction, price: Price):

        self.transaction = transaction
        self.price = price
        self.transaction_dates = transaction.dates
        self.price_dates = price.dates
        self.tickers = price.tickers
        self.dataframe = pd.DataFrame



    def value_positions(self) -> None:

        # A quick analysis shows that transactions and prices don't share all dates
        # For example, there might be dates for which transactions have been recorded but not prices. Therefore, we need to tackle that issue before computing the value
        # For those cases, the idea is to take the lastest recorded price before that date (e.g: if price is missing on 2024-06-07, we take the one from 2024-06-06 if it exists)
        
        # Step 0 - Make sure px_csv is flattened (i.e unpivot_dataframe is not None)
        is_dataframe_empty(self.price.unpivot_dataframe, Price.unpivot)

        # Step 1 - Get all dates from tx_csv and px_csv
        all_dates = self.transaction_dates + self.price_dates

        # Step 2 - Remove duplicates
        all_dates = set(all_dates)

        # Step 3 - Sort dates by ascending order
        all_dates = sorted(all_dates)

        # Now, the idea is to create a dataframe of all possible combinations of dates and tickers, merge both dataframes on it and fill 'price' null values
        
        # Step 4 - Create a dataframe of all possible combinations of dates and tickers
        self.dataframe = pd.MultiIndex.from_product([all_dates, self.tickers], names=['date', 'ticker']).to_frame(index=False)

        # Step 5 - Merge transaction.dataframe on dataframe using 'date' and 'ticker' attributes
        self.dataframe = pd.merge(self.dataframe, self.transaction.dataframe, how='left', on=['date', 'ticker'])

        # Step 6 - Merge price.unpivot_dataframe on dataframe using 'date' and 'ticker'
        self.price.unpivot_dataframe.rename(columns={'Date':'date'}, inplace=True)
        self.dataframe = pd.merge(self.dataframe, self.price.unpivot_dataframe, how='left', on=['date','ticker'])

        # Step 7 - ffill, meaning 'forward fill', to fill price null values with the latest recorded price before that date
        self.dataframe = self.dataframe.sort_values(by='date')
        self.dataframe['price'] = self.dataframe.groupby('ticker')['price'].ffill()

        # Step 8 - We keep only rows for which we have a transaction
        self.dataframe = self.dataframe[ self.dataframe['order'].isna() == False ]

        # Step 9 - Value positions 
        self.dataframe['value'] = self.dataframe['position'] * self.dataframe['price']

        return self



    def calculate_performance(self, columns, agg, suffix) -> pd.DataFrame:
    
        # Step 1 - Make sure dataframe is is not None (i.e value_positions was run before calling that function)
        is_dataframe_empty(self.dataframe, self.value_positions)

        portfolio_copy = copy.deepcopy(self.dataframe)
        portfolio_grouped = portfolio_copy.groupby(columns).agg(agg).reset_index()


        if 'ticker' in columns:

            if 'value' in agg and 'price' in agg:
                portfolio_grouped.columns = columns + ['value_sum', 'price_mean', 'price_std']
                portfolio_grouped.rename(columns={
                    'value_sum': f'ticker_{suffix}_value',
                    'price_mean': f'ticker_{suffix}_price_mean',
                    'price_std': f'ticker_{suffix}_price_std'
                }, inplace=True)

        else:

            if 'value' in agg:
                portfolio_grouped[f'prev_portfolio_{suffix}_value'] = portfolio_grouped['value'].shift(1)
                portfolio_grouped[f'portfolio_{suffix}_performance_USD'] = portfolio_grouped['value'] - portfolio_grouped[f'prev_portfolio_{suffix}_value']
                portfolio_grouped[f'portfolio_{suffix}_performance_pct'] = 100 * portfolio_grouped[f'portfolio_{suffix}_performance_USD'] / portfolio_grouped[f'prev_portfolio_{suffix}_value']
                portfolio_grouped.rename(columns={'value': f'portfolio_{suffix}_value'}, inplace=True)

        return portfolio_grouped