import pandas as pd
from index_monkey.model import engine
import datetime


DBMF_HOLDINGS_LINK = 'https://partnerselectfunds.com/wp-content/uploads/Holdings/DBMF-Holdings.xlsx'


def pull_dbmf_holdings():
    dbmf_df = pd.read_excel(DBMF_HOLDINGS_LINK, skiprows=5)
    dbmf_df = dbmf_df[['DATE', 'CUSIP', 'TICKER', 'DESCRIPTION', 'SHARES', 'BASE_MV',
                       'PCT_HOLDINGS']]
    dbmf_df['DATE'] = dbmf_df['DATE'].apply(lambda dt: datetime.datetime.strptime(str(dt), '%Y%m%d').date())
    dbmf_df = dbmf_df.rename(columns={'DATE': 'hdate',
                                      'CUSIP': 'cusip',
                                      'TICKER': 'ticker',
                                      'DESCRIPTION': 'description',
                                      'SHARES': 'shares',
                                      'BASE_MV': 'mv',
                                      'PCT_HOLDINGS': 'weight'})
    return dbmf_df


def insert_dbmf_holdings(dbmf_holdings):
    dbmf_holdings.to_sql('dbmf_holdings', con=engine, if_exists='append', index=False)


if __name__ == '__main__':
    dbmf_hldgs = pull_dbmf_holdings()
    insert_dbmf_holdings(dbmf_hldgs)
