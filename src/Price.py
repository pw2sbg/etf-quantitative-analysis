import pandas as pd
import copy
from config.constants import px_csv
from src.File import File
from lib.utils import *



class Price(File):



    def __init__(self, file_name: str):
        
        super().__init__(file_name)

        # Sanity checks
        check_file_name(px_csv, self.file_name)
        self.check_headers()

        # Once checks passed
        self.dates = list(self.dataframe['Date'].unique())
        self.tickers = self.get_tickers()
        self.unpivot_dataframe = pd.DataFrame



    def get_tickers(self) -> list[str]:
        tickers = copy.deepcopy(self.headers)
        tickers.remove('Date')
        return tickers



    def unpivot(self) -> None:

        # In order to compute the value of the positions, we need to merge prices on transactions for each date and ticker
        # This is not possible yet because tickers are headers in px_csv while it is a column in tx_csv
        # So we have to 'unpivot'/'flatten' px_csv before merging it on tx_etf

        # Instead of updating the dataframe, I set a new datarframe (i.e unpivot_dataframe) which is updated when this function is run
        # So, we can make sure the dataframe is unpivoted before merging it on tx_csv dataframe (see is_pivot method) 
        
        # N.B: Does not return a dataframe but the updated unpivot_dataframe

        self.unpivot_dataframe = pd.melt(self.dataframe, id_vars='Date', value_vars=self.tickers, var_name='ticker', value_name='price') 
        
        # Sanity checks
        check_ticker_values(self.unpivot_dataframe)
        check_column_type(self.unpivot_dataframe, 'price', 'float64')
        check_negative_values(self.unpivot_dataframe, 'price')

        return self

 

    def check_headers(self):
        if 'Date' not in self.headers:
            raise ValueError('Missing "Date" column')
        else:
            if len(self.headers) == 1:
                raise ValueError('Missing tickers')