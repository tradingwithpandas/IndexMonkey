import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
# from index_monkey.analysis.seasonality import get_historic_specific_month_performance
from index_monkey.analysis.seasonality import get_monthly_performance, get_avg_monthly_performance
import yfinance as yf

MONTH_MAP = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec',
}


def plot_monthly_performance(ticker, start_date, end_date):
    monthly_perf = get_monthly_performance(ticker, start_date, end_date, as_pct_change=True)
    monthly_perf['Year'] = monthly_perf['Date'].apply(lambda dt: dt.year)
    monthyly_avg_perf = get_avg_monthly_performance(ticker, start_date, end_date)

    fig, ax = plt.subplots(figsize=(20, 10))
    num_years = len(monthly_perf['Year'].unique())

    ax = sns.barplot(data=monthly_perf, x='Month', y='Close', hue='Year')
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=2))
    y_max = max(monthly_perf['Close'])
    y_min = min(monthly_perf['Close'])
    y_inc = abs((y_max - y_min) * 0.1)
    y_lim_min = y_min - y_inc
    y_lim_max = y_max + y_inc
    ax.set(ylim=(y_lim_min, y_lim_max))

    ax2 = ax.twinx()
    ax2 = sns.lineplot(data=monthyly_avg_perf, x='Month', y='Close', color='black')
    ax2.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=2))
    ax2.set(ylim=(y_lim_min, y_lim_max))
    plt.title(f'{ticker} monthly returns {start_date} to {end_date}')

#
# def plot_seasonal_performance_between_months(ticker, month1, month2, exclude_years=None):
#     exclude_years = [str(year) for year in exclude_years or []]
#     ticker_returns = get_historic_specific_month_performance(ticker, month1, month2)
#     ticker_returns['Year'] = ticker_returns['Date'].apply(lambda dt: str(dt.to_pydatetime().year))
#     ticker_returns = ticker_returns[~ticker_returns['Year'].isin(exclude_years)]
#     ticker_returns['AvgReturn'] = ticker_returns['Return'].mean()
#     fig, ax = plt.subplots(figsize=(10, 8))
#     month1_name = MONTH_MAP.get(month1)
#     month2_name = MONTH_MAP.get(month2)
#     ax.set_title(f'{ticker} Seasonal Performance in {month1_name}-{month2_name}')
#     fig.autofmt_xdate()
#     graph = sns.barplot(x='Year', y='Return', data=ticker_returns, palette='Blues')
#     sns.lineplot(x='Year', y='AvgReturn', data=ticker_returns)
#     graph.yaxis.set_major_formatter(PercentFormatter(1))
#     sns.despine()
#
#
# def _prepare_data_for_ticker_month_comparison(ticker1, t1_month1, t1_month2, ticker2, t2_month1, t2_month2):
#
#     ticker1_data = get_historic_specific_month_performance(ticker1, t1_month1, t1_month2)
#     ticker1_data['Year'] = ticker1_data['Date'].dt.year
#     ticker1_data['Year'] = ticker1_data['Year'].apply(str)
#     display_ticker1 = '' if ticker1 == ticker2 else ticker1
#     t1_m1_name = MONTH_MAP.get(t1_month1)
#     t1_m2_name = MONTH_MAP.get(t1_month2)
#     ticker1_data['Window'] = f'{display_ticker1} {t1_m1_name}-{t1_m2_name}'.strip()
#
#     ticker2_data = get_historic_specific_month_performance(ticker2, t2_month1, t2_month2)
#     ticker2_data['Year'] = ticker2_data['Date'].dt.year
#     ticker2_data['Year'] = ticker2_data['Year']
#     ticker2_data['Year'] = ticker2_data['Year'].apply(str)
#     display_ticker2 = '' if ticker1 == ticker2 else ticker2
#     t2_m1_name = MONTH_MAP.get(t2_month1)
#     t2_m2_name = MONTH_MAP.get(t2_month2)
#     ticker2_data['Window'] = f'{display_ticker2} {t2_m1_name}-{t2_m2_name}'.strip()
#
#     combined_data = pd.concat([ticker1_data, ticker2_data])
#     ticker1_years = ticker1_data['Year'].unique()
#     ticker2_years = ticker2_data['Year'].unique()
#     common_years = set(ticker1_years).intersection(set(ticker2_years))
#     combined_data = combined_data[combined_data['Year'].isin(common_years)]
#
#     avg_returns = combined_data.groupby('Window').agg({'Return': 'mean'}).rename(columns={'Return': 'AvgReturn'})
#     combined_data = pd.merge(combined_data, avg_returns, left_on='Window', right_index=True)
#     return combined_data


# def plot_seasonal_performance_between_tickers_and_months(ticker1,
#                                                          t1_month1,
#                                                          t1_month2,
#                                                          ticker2,
#                                                          t2_month1,
#                                                          t2_month2,
#                                                          save_file_name=''
#                                                          ):
#     '''
#     Function to create a Seaborn barplot to compare side by side, the average performance of 2 tickers between 2
#     specific months of every year since it started trading. Example below
#
#     >>> plot_seasonal_performance_between_tickers_and_months('XBI', 12, 1, 'XBI', 1, 2, save_file_name='chart.png')
#
#
#     :param ticker1:
#     :param t1_month1:
#     :param t1_month2:
#     :param ticker2:
#     :param t2_month1:
#     :param t2_month2:
#     :param save_file_name:
#     :return:
#     '''
#     combined_data = _prepare_data_for_ticker_month_comparison(ticker1, t1_month1, t1_month2, ticker2, t2_month1,
#                                                               t2_month2)
#     fig, ax = plt.subplots(figsize=(10, 8))
#     fig.autofmt_xdate()
#     chart_title_month_str = 'Comparison across months' if t1_month1 != t2_month1 and t1_month2 != t2_month2 else ''
#     if ticker1 != ticker2:
#         chart_title = f'{ticker1} vs {ticker2} {chart_title_month_str}'
#     else:
#         chart_title = f'{ticker1} {chart_title_month_str}'
#     ax.set_title(chart_title)
#
#     graph = sns.barplot(x='Year', y='Return', data=combined_data, hue='Window', palette='Blues')
#     sns.lineplot(x='Year', y='AvgReturn', data=combined_data, hue='Window', palette='Blues')
#     plt.legend(loc='best')
#     graph.yaxis.set_major_formatter(PercentFormatter(1))
#     sns.despine()
#     if save_file_name:
#         plt.savefig(save_file_name)


def two_asset_chart(ticker1, ticker2, start_date, end_date, ticker1_df_override=None, ticker2_df_override=None):
    tk1 = yf.Ticker(ticker1)
    tk2 = yf.Ticker(ticker2)

    passed_valid_ticker1_override = ticker1_df_override is not None and not ticker1_df_override.empty
    tk1_hist = ticker1_df_override if passed_valid_ticker1_override else tk1.history(start=start_date, end=end_date)
    tk1_hist = tk1_hist[start_date:end_date]
    tk1_hist = tk1_hist.reset_index()
    passed_valid_ticker2_override = ticker2_df_override is not None and not ticker2_df_override.empty
    tk2_hist = ticker2_df_override if passed_valid_ticker2_override else tk2.history(start=start_date, end=end_date)
    tk2_hist = tk2_hist[start_date:end_date]
    tk2_hist = tk2_hist.reset_index()

    fig, ax = plt.subplots(figsize=(16, 10))
    fig.autofmt_xdate()
    graph = sns.lineplot(x='Date', y='Close', data=tk1_hist, color='blue')
    graph2 = graph.twinx()
    graph2 = sns.lineplot(x='Date', y='Close', data=tk2_hist, color='green')
    # ax.legend([graph, graph2], [ticker1, ticker2], loc=0)
    ax.legend()
