import os
import pandas as pd
from config.constants import tx_csv, px_csv, start_year, start_year_month, end_year, end_year_month
from src.Transaction import Transaction
from src.Price import Price
from src.Portfolio import Portfolio
from lib.utils import evolution, composition




# Instantiate classes
transaction = Transaction(tx_csv)
price = Price(px_csv)
print('Transaction and Price classes instantiated')




# Reconstruct positions and unpivot px_etf to be able to value positions
transaction.reconstruct_positions()
price.unpivot()
print('Positions reconstructed')




# Value positions 
portfolio = Portfolio(transaction, price)
portfolio.value_positions()
print('Positions evaluated')




# Convert 'date' column from 'portfolio' into datetime to extract year and month
portfolio.dataframe['date'] = pd.to_datetime(portfolio.dataframe['date'], format='%Y-%m-%d')
portfolio.dataframe['year'] = portfolio.dataframe['date'].dt.year
portfolio.dataframe['month'] = portfolio.dataframe['date'].dt.month




grouping_configs = [
    {
        'columns': ['year', 'ticker'],
        'agg': {'value': 'sum', 'price': ['mean', 'std']},
        'suffix': 'yearly'
    },
    {
        'columns': ['year', 'month', 'ticker'],
        'agg': {'value': 'sum', 'price': ['mean', 'std']},
        'suffix': 'monthly'
    },
    {
        'columns': ['year'],
        'agg': {'value': 'sum'},
        'suffix': 'yearly'
    },
    {
        'columns': ['year', 'month'],
        'agg': {'value': 'sum'},
        'suffix': 'monthly'
    }
]


# Process each configuration and store the results depending on the suffix (i.e: monthly, yearly)
yearly_results = []
monthly_results = []
for config in grouping_configs:
    columns = config['columns']
    agg = config['agg']
    suffix = config['suffix']
    result = portfolio.calculate_performance(columns, agg, suffix)
    if suffix == 'yearly':
        yearly_results.append(result)
    elif suffix == 'monthly':
        result['year_month'] = result['year'] * 100 + result['month']
        monthly_results.append(result)
print('Yearly and monthly performance calculated')




# Merge all monthly results
if monthly_results:
    monthly_performance = monthly_results[0]
    for df in monthly_results[1:]:
        monthly_performance = pd.merge(monthly_performance, df, how='left', on=['year', 'month', 'year_month'])




# Merge all yearly results
if yearly_results:
    yearly_performance = yearly_results[0]
    for df in yearly_results[1:]:
        yearly_performance = pd.merge(yearly_performance, df, how='left', on=['year'])





# Create 'output' folder to store csv files if it does not exist
current_directory = os.getcwd()
if 'output' not in os.listdir():
    os.mkdir(os.path.join(current_directory, 'output'))
    print(f'Folder named "output" created in current directory: {current_directory}')



# Convert dataframes into csv and save them in the 'output' folder
monthly_performance.to_csv(os.path.join(current_directory, 'output', 'monthly.csv'))
print(f'Monthly performance saved as csv in: {os.path.join(current_directory, "output", "monthly.csv")}')

yearly_performance.to_csv(os.path.join(current_directory, 'output', 'yearly.csv'))
print(f'Yearly performance saved as csv in: {os.path.join(current_directory, "output", "yearly.csv")}')




# Chart of Portfolio monthly evolution in USD and pct (%) (for the given dates: start_year_month - end_year_month), saved in 'output' folder as a png image
evolution(df=monthly_performance, start=start_year_month, end=end_year_month, unit='USD', save_path=os.path.join(current_directory, 'output', f'evolution_{start_year_month}_{end_year_month}_USD.png'))
evolution(df=monthly_performance, start=start_year_month, end=end_year_month, unit='pct', save_path=os.path.join(current_directory, 'output', f'evolution_{start_year_month}_{end_year_month}_pct.png'))

# Chart of Portfolio yearly evolution in USD and pct (%) (for the given dates: start_year - end_year), saved in 'output' folder as a png image
evolution(df=yearly_performance, start=start_year, end=end_year, unit='USD', save_path=os.path.join(current_directory, 'output', f'evolution_{start_year}_{end_year}_USD.png'))
evolution(df=yearly_performance, start=start_year, end=end_year, unit='pct', save_path=os.path.join(current_directory, 'output', f'evolution_{start_year}_{end_year}_pct.png'))

# Chart of Portfolio monthly and yearly composition (for the given dates: start_year and start_year_month), saved in 'output' folder as a png image
composition(df=monthly_performance, date=start_year_month, save_path=os.path.join(current_directory, 'output', f'composition_{start_year_month}.png'))
composition(df=yearly_performance, date=start_year, save_path=os.path.join(current_directory, 'output', f'composition_{start_year}.png'))