import sqlite3
from functools import lru_cache
from json.decoder import JSONDecodeError

import pandas as pd
import yfinance as yf

from index_monkey.constants import DB_NAME
from index_monkey.model import engine
from index_monkey.reader import PriceReader


@lru_cache()
def connection():
    return sqlite3.connect(DB_NAME)


class PriceLoader(PriceReader):

    def __init__(self, indexname, start_date=None, end_date=None):
        super().__init__(indexname, start_date, end_date)
        self._loaded_prices = None

    @property
    def loaded_prices(self):
        return self._loaded_prices

    @loaded_prices.setter
    def loaded_prices(self, value):
        self._loaded_prices = value

    @staticmethod
    def save_prices(prices_df):
        prices_df.to_sql('stock_prices', con=engine, if_exists='append', index=False)

    @staticmethod
    def is_date_range_covered(start_date_in_db, end_date_in_db, query_start_date, query_end_date):
        return query_start_date <= start_date_in_db and end_date_in_db >= query_end_date

    def _generate_yf_query_args_based_on_data_in_db(self, data_in_db, tickers, start_date, end_date, refresh):
        yf_query_args = {}
        for ticker in tickers:
            ticker_df = data_in_db[data_in_db['ticker'] == ticker]
            if not refresh:
                if not ticker_df.empty:
                    ticker_start_date = ticker_df['pdate'].min().to_pydatetime().date()
                    ticker_end_date = ticker_df['pdate'].max().to_pydatetime().date()
                    if self.is_date_range_covered(ticker_start_date, ticker_end_date, start_date, end_date):
                        # No need to query from YF again in this case. Just use what we got from the DB
                        continue
            yf_query_args[ticker] = {'start': start_date, 'end': end_date}
        return yf_query_args

    def _load_ticker_data_from_yf(self, tickers, start_date=None, end_date=None, refresh=False):
        start_date = start_date or self.start_date
        end_date = end_date or self.end_date
        query = self.construct_query(tickers, start_date, end_date)
        full_px_history = self.load(query)

        ticker_yf_args = self._generate_yf_query_args_based_on_data_in_db(full_px_history,
                                                                          tickers,
                                                                          start_date,
                                                                          end_date,
                                                                          refresh)
        errored_tickers = []

        for index, (ticker, yf_args) in enumerate(ticker_yf_args.items()):
            yf_ticker = yf.Ticker(ticker)

            try:
                px_hist = yf_ticker.history(**yf_args)
            except JSONDecodeError:
                errored_tickers.append(ticker)
                continue

            px_hist['ticker'] = ticker
            px_hist = px_hist.reset_index()
            px_hist = px_hist.rename(columns={'Date': 'pdate', 'Open': 'open', 'High': 'high', 'Low': 'low',
                                              'Close': 'close', 'Volume': 'volume', 'Dividends': 'dividends',
                                              'Stock Splits': 'stock_splits'})
            px_hist = px_hist[['pdate', 'ticker', 'open', 'high', 'low', 'close', 'volume', 'stock_splits']]
            if full_px_history is not None:
                full_px_history = pd.concat([full_px_history, px_hist])
            else:
                full_px_history = px_hist

        return full_px_history, errored_tickers

    def _load_prices_from_yf(self):
        full_px_history = None
        input_tickers = self.tickers

        while input_tickers:
            px_hist, errored_tickers = self._load_ticker_data_from_yf(input_tickers)

            if full_px_history is None:
                full_px_history = px_hist
            else:
                full_px_history = pd.concat([full_px_history, px_hist])

            input_tickers = errored_tickers
            print(f'{len(self.tickers) - len(errored_tickers)} / {len(self.tickers)} Downloaded')

        self.loaded_prices = full_px_history
        return full_px_history

    # def _load_prices_from_yf_bulk(self, min_step=51):
    #     member_df = self.member_reader.load()
    #     tickers = member_df['Symbol'].unique().tolist()
    #     full_px_history = None
    #     px_hist_kwargs = {'threads': False, 'group_by': 'ticker'}
    #     if self.start_date:
    #         px_hist_kwargs['start'] = self.start_date.strftime('%Y-%m-%d')
    #     if self.end_date:
    #         px_hist_kwargs['end'] = self.end_date.strftime('%Y-%m-%d')
    #     if not px_hist_kwargs:
    #         px_hist_kwargs['period'] = 'max'
    #     ticker_lists = split_list(tickers, min_step)
    #
    #     for ticker_list in ticker_lists:
    #         tickers_str = ' '.join(ticker_list)
    #         px_hist = yf.download(tickers_str, **px_hist_kwargs)
    #         px_hist = px_hist.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)
    #         if full_px_history is not None:
    #             full_px_history = pd.concat(full_px_history, px_hist)
    #         else:
    #             full_px_history = px_hist
    #
    #     self.loaded_prices = full_px_history
    #     return full_px_history
