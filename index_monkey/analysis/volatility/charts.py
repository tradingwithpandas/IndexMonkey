import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
from . import volatility_histogram_df
import datetime
import pandas as pd


def chart_volatility_histogram(ticker: str,
                               return_window: str = 'Y',
                               start_date: datetime.date = None,
                               end_date: datetime.date = None,
                               num_buckets: int = 10,
                               px_hist_override: pd.DataFrame = None):
    vol_hist_df = volatility_histogram_df(ticker, return_window, start_date, end_date, num_buckets,
                                          px_hist_override=px_hist_override)
    fig, ax = plt.subplots(figsize=(12, 10))
    total_num_of_years = vol_hist_df['frequency_count'].sum()
    ax.set_title(f'{ticker} Historic Volatility ({total_num_of_years} years)')
    fig.autofmt_xdate()
    graph = sns.barplot(x='freq_str', y='Return', data=vol_hist_df, palette='Blues')
    plt.xlabel = 'Frequency\nReturn'
    graph.yaxis.set_major_formatter(PercentFormatter(1))
