import pandas as pd
from pandas.tseries.offsets import BDay
from talib.abstract import *

from index_monkey.reader import PriceReader


def get_sma(ticker_px, ticker, date_col='pdate', px_col='close', timeperiod=200):
    ticker_px = ticker_px.sort_values(date_col)
    ticker_px = ticker_px.set_index(date_col)
    sma_fn = Function('SMA')
    ticker_sma = sma_fn(ticker_px, timeperiod=timeperiod, price=px_col)
    ticker_sma = ticker_sma.reset_index()
    ticker_sma = ticker_sma.rename(columns={0: f'{timeperiod}DSMA'})
    ticker_sma['ticker'] = ticker
    return ticker_sma


def get_sma_on_index(index_name, start_date=None, end_date=None, use_latest_index_weighting=False,
                     timeperiods=(50, 200)):
    index_start_date = None if use_latest_index_weighting else start_date
    index_end_date = None if use_latest_index_weighting else end_date
    adj_start_date = start_date
    if start_date:
        max_timeperiod = max(timeperiods) + 20
        adj_start_date = start_date - BDay(max_timeperiod)
        adj_start_date = adj_start_date.to_pydatetime()
    px_reader = PriceReader(index_name, adj_start_date, end_date, index_start_date, index_end_date,
                            use_latest_index_weighting=use_latest_index_weighting)
    px_df = px_reader.load()
    px_with_sma_df = pd.DataFrame()
    tickers = px_df['ticker'].unique()
    for ticker in tickers:
        ticker_px = px_df[px_df['ticker'] == ticker]
        for timeperiod in timeperiods:
            sma_df = get_sma(ticker_px, ticker, timeperiod=timeperiod)
            ticker_px = pd.merge(ticker_px, sma_df, left_on=['pdate', 'ticker'], right_on=['pdate', 'ticker'])
        px_with_sma_df = pd.concat([px_with_sma_df, ticker_px])
    return px_with_sma_df


def get_pct_above_ma(index_name,
                     start_date=None,
                     end_date=None,
                     timeperiods=(50, 200),
                     use_latest_index_weighting=False,
                     sector_lvl=False):
    index_smas = get_sma_on_index(index_name, start_date=start_date, end_date=end_date,
                                  use_latest_index_weighting=use_latest_index_weighting, timeperiods=timeperiods)
    for timeperiod in timeperiods:
        index_smas[f'Above{timeperiod}DSMA'] = index_smas['close'] > index_smas[f'{timeperiod}DSMA']
        index_smas[f'Above{timeperiod}DSMA'] = index_smas[f'Above{timeperiod}DSMA'].apply(int)
    groupby_agg = {f'NumAbove{timeperiod}DSMA': (f'Above{timeperiod}DSMA', 'sum') for timeperiod in timeperiods}
    groupby_agg['Total'] = ('ticker', 'count')
    groupby_key = ['pdate', 'sector'] if sector_lvl else ['pdate']
    index_smas = index_smas.groupby(groupby_key).agg(**groupby_agg)
    for timeperiod in timeperiods:
        index_smas[f'PctAbove{timeperiod}DSMA'] = index_smas[f'NumAbove{timeperiod}DSMA'] / index_smas['Total']
    if start_date and sector_lvl:
        index_smas = index_smas.reset_index(level=1)
        index_smas = index_smas.loc[start_date.strftime('%Y-%m-%d'):]
        index_smas = index_smas.reset_index()
        index_smas = index_smas.set_index(['pdate', 'sector'])
    elif start_date:
        index_smas = index_smas.loc[start_date.strftime('%Y-%m-%d'):]
    return index_smas
