import pandas as pd
from index_monkey.model import engine, session, DBMFHoldings, ETFStats
import datetime


DBMF_HOLDINGS_LINK = 'https://partnerselectfunds.com/wp-content/uploads/Holdings/DBMF-Holdings.xlsx'


def pull_dbmf_etf_stats():
    dbmf_df = pd.read_excel(DBMF_HOLDINGS_LINK, skiprows=2)
    dbmf_df = dbmf_df[:1]
    dbmf_holdings = pull_dbmf_holdings()
    most_recent_date = dbmf_holdings['hdate'].unique()[0]
    dbmf_df['sdate'] = most_recent_date
    dbmf_df['ticker'] = 'DBMF'
    dbmf_df = dbmf_df.rename(columns={'NAV': 'nav', 'SHARES_OUTSTANDING': 'shares_outstanding',
                                      'TOTAL_NET_ASSETS': 'aum'})
    dbmf_df = dbmf_df[['sdate', 'ticker', 'nav', 'shares_outstanding', 'aum']]
    return dbmf_df


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


def fetch_holdings_on_date(holding_date):
    db_session = session()
    query = db_session.query(DBMFHoldings).filter(DBMFHoldings.hdate == holding_date)
    holdings_df = pd.read_sql(query.statement, engine)
    return holdings_df


def fetch_stats_on_date(stat_date, ticker):
    db_session = session()
    query = db_session.query(ETFStats).filter(ETFStats.sdate == stat_date).filter(ETFStats.ticker == ticker)
    stat_df = pd.read_sql(query.statement, engine)
    return stat_df


def date_has_holdings(holding_date, df_fetch_fn, date_col, **kwargs):
    most_recent_holdings = df_fetch_fn(holding_date, **kwargs)
    if not most_recent_holdings.empty:
        holding_date = most_recent_holdings[date_col].unique()[0]
    else:
        holding_date = None
    return holding_date


def insert_dbmf_holdings(dbmf_holdings):
    holding_date = dbmf_holdings['hdate'].unique()[0] if dbmf_holdings['hdate'].unique() else None
    # Data for this date doesn't exist already and hence we need to store this data
    if not date_has_holdings(holding_date, fetch_holdings_on_date, 'hdate'):
        dbmf_holdings.to_sql('dbmf_holdings', con=engine, if_exists='append', index=False)


def insert_dbmf_stats(dbmf_stats):
    stat_date = dbmf_stats['sdate'].unique()[0] if dbmf_stats['sdate'].unique() else None
    # Data for this date doesn't exist already and hence we need to store this data
    if not date_has_holdings(stat_date, fetch_stats_on_date, 'sdate', ticker='DBMF'):
        dbmf_stats.to_sql('etf_stats', con=engine, if_exists='append', index=False)


if __name__ == '__main__':
    dbmf_hldgs = pull_dbmf_holdings()
    insert_dbmf_holdings(dbmf_hldgs)

    dbmf_stats = pull_dbmf_etf_stats()
    insert_dbmf_stats(dbmf_stats)

