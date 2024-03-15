import yfinance as yf
import datetime
from index_monkey.utils import check_valid_month, get_first_biz_day_of_month
import pandas as pd


def get_monthly_performance(ticker, start_date, end_date, as_pct_change=True):
    ticker_px = yf.Ticker(ticker).history(start=start_date, end=end_date)
    if not ticker_px.empty:
        ticker_px = ticker_px.asfreq(freq='BM')['Close']
        if as_pct_change:
            ticker_px = ticker_px.pct_change()
        ticker_px = ticker_px.reset_index()
        ticker_px['Month'] = pd.Categorical(ticker_px['Date'].apply(lambda dt: dt.strftime('%b')),
                                            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                                             'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ticker_px = ticker_px[ticker_px['Close'].notnull()]
    else:
        ticker_px = pd.DataFrame(columns=['Month', 'Close'])
    return ticker_px


def get_avg_monthly_performance(ticker, start_date, end_date, outlier_threshold=None):
    monthly_performance = get_monthly_performance(ticker, start_date, end_date, as_pct_change=True)
    if outlier_threshold is not None:
        monthly_performance = monthly_performance[~((monthly_performance['Close'] > outlier_threshold) | (monthly_performance['Close'] < outlier_threshold * -1))]
    monthly_avg_perf = monthly_performance.groupby('Month')['Close'].mean()
    monthly_avg_perf = monthly_avg_perf.reset_index()
    monthly_avg_perf = monthly_avg_perf.sort_values(['Month'])
    return monthly_avg_perf
