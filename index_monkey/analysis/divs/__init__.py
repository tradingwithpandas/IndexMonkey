import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import yfinance as yf
import datetime
from pprint import pprint
from functools import lru_cache

CCY_DIVISORS = {
    'GBp': 100,
}


@lru_cache(maxsize=None)
def get_yf_ticker(ticker):
    if isinstance(ticker, str):
        ticker = yf.Ticker(ticker)
    elif isinstance(ticker, yf.Ticker):
        pass
    return ticker


@lru_cache(maxsize=None)
def get_price_history(ticker, period='10y'):
    ticker = get_yf_ticker(ticker)
    ticker_hist = ticker.history(period=period)
    ticker_hist.reset_index(level=0, inplace=True)
    return ticker_hist


def get_div_adj_return(ticker, amt=0, qty=0, period='10y'):
    ticker = get_yf_ticker(ticker)
    ccy_divisor = ticker.get_info().get(ccy)
    ticker_hist = ticker.history(period=period)
    start_price = ticker_hist.iloc[0]['Close']
    if amt:
        if ccy_divisor:
            start_price /= ccy_divisor
        qty += amt / start_price


def get_total_return(ticker, qty, period='10y'):
    ticker = get_yf_ticker(ticker)
    ccy_divisor = CCY_DIVISORS.get(ticker.get_info().get('currency')) or 1
    ticker_hist = ticker.history(period=period)
    first_row = ticker_hist.head(1).copy()
    # Not eligible for first dividend even if we bought on a pay date
    first_row['Dividends'] = 0
    last_row = ticker_hist.tail(1).copy()
    div_df = ticker_hist[ticker_hist['Dividends'] != 0]
    div_df = pd.concat([first_row, div_df])
    # if last_row is not a div pay date
    if last_row[last_row['Dividends'] != 0].empty:
        div_df = pd.concat([div_df, last_row])
    div = 0
    div_dict = {}
    for index, row in div_df.iterrows():
        div_amt = row['Dividends'] * qty
        div += div_amt
        if div > row['Close']:
            new_shs = int(div / row['Close'])
            div = div - (new_shs * row['Close'])
            qty += new_shs
        div_dict[index.date()] = {'qty': qty, 'div_cash': div / ccy_divisor, 'mv': qty * row['Close'] / ccy_divisor,
                                  'Close': row['Close']}
    ticker_div_df = pd.DataFrame(div_dict).transpose()
    ticker_div_df.reset_index(level=0, inplace=True)
    ticker_div_df.rename(columns={'index': 'Date'}, inplace=True)
    return ticker_div_df
