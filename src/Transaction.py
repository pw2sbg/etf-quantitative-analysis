from src.File import File
from lib.utils import *
from config.constants import tx_csv, tx_headers
import numpy as np



class Transaction(File):



    def __init__(self, file_name: str):
        
        super().__init__(file_name)

        # Sanity checks
        check_file_name(tx_csv, self.file_name)
        self.check_headers()
        check_ticker_values(self.dataframe)
        check_column_type(self.dataframe, 'qty', 'int64')
        check_negative_values(self.dataframe, 'qty')
        self.check_order_values()

        # Once checks passed 
        self.dates = list(self.dataframe['date'].unique())


    
    def reconstruct_positions(self) -> None:

        # A position is the amount of a particular security, commodity or currency held or owned by a person or entity
        # As for each transaction, we know the date, the order, the quantity and the ticker, we can compute the positions for each ticker
        # The idea is:
        # - to convert first the absolute quantities into 'relative' based on the order (i.e 'BUY' = +qty, 'SELL' = -qty)
        # - to be able then to compute a cumulative sum over those relative quantities for each ticker

        # N.B: Does not return a dataframe but update the dataframe with the positions calculated
        
        # Step 1 - Sort dataframe by ascending date
        self.dataframe = self.dataframe.sort_values(by='date')   

        # Step 2 - Convert absolute quantities into relative 
        self.dataframe['relative_qty'] = np.where(self.dataframe['order'] == 'BUY', self.dataframe['qty'], -self.dataframe['qty'])
        
        # Step 3 - Compute cumulative sum for each ticker
        self.dataframe['position'] = self.dataframe.groupby('ticker')['relative_qty'].cumsum()

        # Step 4 - Drop columns which are not necessary anymore
        # Commented so one can check the good reconstruction of the positions. 
        # self.dataframe.drop(['order', 'relative_qty'], inplace = True)

        # Remark - One could also simply update dataframe['position'] as follows:
        # self.dataframe['position'] = np.where(self.dataframe['order'] == 'BUY', self.dataframe['qty'], -self.dataframe['qty'])
        # self.dataframe['position'] = self.dataframe.groupby('ticker')['relative_qty'].cumsum()

        return self
    

    def check_headers(self):
        for header in tx_headers:
            if header not in self.headers:
                raise ValueError(f'Missing {header} in headers. Headers should be {tx_headers}')
        

    def check_order_values(self):
        order_unique_values_sorted = sorted(list(self.dataframe['order'].unique())) 
        if order_unique_values_sorted != ['BUY', 'SELL']:
            raise ValueError(f'order column should only contain "BUY" and "SELL" values. Got {order_unique_values_sorted}')