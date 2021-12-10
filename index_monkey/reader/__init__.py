import datetime
import sqlite3
from functools import lru_cache

import pandas as pd

from ..constants import DB_NAME


@lru_cache()
def connection():
    return sqlite3.connect(DB_NAME)


class MembershipReader:

    def __init__(self, ticker, start_date=None, end_date=None, load_on_init=True):
        self.ticker = ticker
        self._start_date_for_query = start_date
        self._end_date_for_query = end_date
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
        if self._end_date_for_query and self._start_date_for_query:
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

    def __init__(self, indexname, start_date=None, end_date=None):
        self.indexname = indexname
        self.member_reader = MembershipReader(self.indexname, start_date=start_date, end_date=end_date)
        self.member_df = self.member_reader.load()
        self.start_date = self.member_reader.start_date
        self.end_date = self.member_reader.end_date
        self._loaded_prices = None

    @property
    def tickers(self):
        return self.member_df['ticker'].unique().tolist()

    def construct_query(self, tickers=None, start_date=None, end_date=None):
        tickers = tickers or self.tickers
        start_date = start_date or self.start_date
        end_date = end_date or self.end_date
        tickers_str = ', '.join([f'\'{ticker}\'' for ticker in set(tickers)])
        return f'''
            SELECT * FROM stock_prices sp
            WHERE sp.ticker IN ({tickers_str})
            AND sp.pdate BETWEEN '{start_date}' AND '{end_date}'
            '''

    def load(self, query=None):
        query = query or self.construct_query()
        return pd.read_sql_query(query, connection(), parse_dates={'pdate': '%Y-%m-%d'})
