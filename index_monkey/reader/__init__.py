import datetime
import sqlite3
from functools import lru_cache

import pandas as pd

from ..constants import DB_NAME
from ..ref_data import TICKER_MAP


@lru_cache()
def connection():
    return sqlite3.connect(DB_NAME)


def get_sectors(index_name):
    query = f'''
    SELECT
    DISTINCT im.sector
    FROM index_membership im
    WHERE im.index_name = '{index_name}'
    '''
    df = pd.read_sql_query(query, connection())
    sectors = df['sector'].unique()
    return sectors


class MembershipReader:

    def __init__(self, ticker, start_date=None, end_date=None, load_on_init=True, use_latest_date=False):
        self.ticker = TICKER_MAP.get(ticker) or ticker
        self._start_date_for_query = start_date
        self._end_date_for_query = end_date
        self._use_latest_date = use_latest_date
        self._df = self.load() if load_on_init else None

    @property
    def start_date(self):
        start_date = None
        if self._start_date_for_query:
            start_date = self._start_date_for_query
        elif isinstance(self._df, pd.DataFrame) and not self._df.empty:
            start_date = self._df['idate'].min().to_pydatetime().date()
        return start_date

    @property
    def end_date(self):
        end_date = datetime.date.today()
        if self._end_date_for_query:
            end_date = self._end_date_for_query
        elif isinstance(self._df, pd.DataFrame) and not self._df.empty:
            end_date = max(datetime.date.today(), self._df['idate'].max().to_pydatetime().date())
        return end_date

    @property
    def query(self):
        ticker_filter = f'WHERE im.indexname = \'{self.ticker}\''
        if self._use_latest_date:
            date_filter = \
                f'AND im.idate = (SELECT MAX(idate) FROM index_membership WHERE indexname = \'{self.ticker}\')'
        elif self._end_date_for_query and self._start_date_for_query:
            date_filter = f'AND im.idate BETWEEN \'{self._start_date_for_query}\' AND \'{self._end_date_for_query}\''
        elif self._end_date_for_query and not self._start_date_for_query:
            date_filter = f'AND im.idate = \'{self._end_date_for_query}\''
        else:
            date_filter = \
                f'AND im.idate = (SELECT MAX(idate) FROM index_membership WHERE indexname = \'{self.ticker}\')'
        return f'''
        SELECT * FROM index_membership im
        {ticker_filter}
        {date_filter}
        ORDER BY im.weight DESC
        '''

    def load(self):
        df = pd.read_sql_query(self.query, connection(), parse_dates={'idate': '%Y-%m-%d'})
        return df


class PriceReader:

    def __init__(self,
                 indexname,
                 start_date=None,
                 end_date=None,
                 index_start_date=None,
                 index_end_date=None,
                 use_latest_index_weighting=False):
        self.indexname = indexname
        self.member_reader = MembershipReader(self.indexname, start_date=index_start_date, end_date=index_end_date,
                                              use_latest_date=use_latest_index_weighting)
        self.member_df = self.member_reader.load()
        self.start_date = start_date
        self.end_date = end_date
        self._loaded_prices = None

    @property
    def tickers(self):
        return self.member_df['ticker'].unique().tolist()

    def construct_query(self, tickers=None, start_date=None, end_date=None):
        tickers = tickers or self.tickers
        start_date = start_date or self.start_date
        end_date = end_date or self.end_date
        date_filter = ''
        if start_date and end_date:
            date_filter = f'AND sp.pdate BETWEEN \'{start_date}\' and \'{end_date}\''
        elif start_date and not end_date:
            date_filter = f'AND sp.pdate >= \'{start_date}\''
        elif end_date and not start_date:
            date_filter = f'AND sp.pdate <= \'{end_date}\''
        tickers_str = ', '.join([f'\'{ticker}\'' for ticker in set(tickers)])
        return f'''
            SELECT * FROM stock_prices sp
            WHERE sp.ticker IN ({tickers_str})
            {date_filter}
            '''

    def load(self, query=None):
        query = query or self.construct_query()
        px_df = pd.read_sql_query(query, connection(), parse_dates={'pdate': '%Y-%m-%d'})
        mem_df = self.member_df[['ticker', 'indexname', 'sector']]
        px_df = pd.merge(px_df, mem_df, left_on='ticker', right_on='ticker')
        px_df = px_df.sort_values('pdate')
        px_df = px_df[['pdate', 'ticker', 'indexname', 'sector', 'open', 'high', 'low', 'close', 'volume', 'dividends',
                       'stock_splits']]
        return px_df
