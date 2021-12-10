import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
from index_monkey.analysis.seasonality import get_historic_specific_month_performance

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


def plot_seasonal_performance_between_months(ticker, month1, month2, exclude_years=None):
    exclude_years = [str(year) for year in exclude_years or []]
    ticker_returns = get_historic_specific_month_performance(ticker, month1, month2)
    ticker_returns['Year'] = ticker_returns['Date'].apply(lambda dt: str(dt.to_pydatetime().year))
    ticker_returns = ticker_returns[~ticker_returns['Year'].isin(exclude_years)]
    ticker_returns['AvgReturn'] = ticker_returns['Return'].mean()
    fig, ax = plt.subplots(figsize=(10, 8))
    month1_name = MONTH_MAP.get(month1)
    month2_name = MONTH_MAP.get(month2)
    ax.set_title(f'{ticker} Seasonal Performance in {month1_name}-{month2_name}')
    fig.autofmt_xdate()
    graph = sns.barplot(x='Year', y='Return', data=ticker_returns, palette='Blues')
    sns.lineplot(x='Year', y='AvgReturn', data=ticker_returns)
    graph.yaxis.set_major_formatter(PercentFormatter(1))
    sns.despine()


def _prepare_data_for_ticker_month_comparison(ticker1, t1_month1, t1_month2, ticker2, t2_month1, t2_month2):

    ticker1_data = get_historic_specific_month_performance(ticker1, t1_month1, t1_month2)
    ticker1_data['Year'] = ticker1_data['Date'].dt.year
    ticker1_data['Year'] = ticker1_data['Year'].apply(str)
    display_ticker1 = '' if ticker1 == ticker2 else ticker1
    t1_m1_name = MONTH_MAP.get(t1_month1)
    t1_m2_name = MONTH_MAP.get(t1_month2)
    ticker1_data['Window'] = f'{display_ticker1} {t1_m1_name}-{t1_m2_name}'.strip()

    ticker2_data = get_historic_specific_month_performance(ticker2, t2_month1, t2_month2)
    ticker2_data['Year'] = ticker2_data['Date'].dt.year
    ticker2_data['Year'] = ticker2_data['Year']
    ticker2_data['Year'] = ticker2_data['Year'].apply(str)
    display_ticker2 = '' if ticker1 == ticker2 else ticker2
    t2_m1_name = MONTH_MAP.get(t2_month1)
    t2_m2_name = MONTH_MAP.get(t2_month2)
    ticker2_data['Window'] = f'{display_ticker2} {t2_m1_name}-{t2_m2_name}'.strip()

    combined_data = pd.concat([ticker1_data, ticker2_data])
    ticker1_years = ticker1_data['Year'].unique()
    ticker2_years = ticker2_data['Year'].unique()
    common_years = set(ticker1_years).intersection(set(ticker2_years))
    combined_data = combined_data[combined_data['Year'].isin(common_years)]

    avg_returns = combined_data.groupby('Window').agg({'Return': 'mean'}).rename(columns={'Return': 'AvgReturn'})
    combined_data = pd.merge(combined_data, avg_returns, left_on='Window', right_index=True)
    return combined_data


def plot_seasonal_performance_between_tickers_and_months(ticker1, t1_month1, t1_month2, ticker2, t2_month1, t2_month2):
    combined_data = _prepare_data_for_ticker_month_comparison(ticker1, t1_month1, t1_month2, ticker2, t2_month1,
                                                              t2_month2)
    fig, ax = plt.subplots(figsize=(10, 8))

    chart_title_month_str = 'Comparison across months' if t1_month1 != t2_month1 and t1_month2 != t2_month2 else ''
    if ticker1 != ticker2:
        chart_title = f'{ticker1} vs {ticker2} {chart_title_month_str}'
    else:
        chart_title = f'{ticker1} {chart_title_month_str}'
    ax.set_title(chart_title)

    graph = sns.barplot(x='Year', y='Return', data=combined_data, hue='Window', palette='Blues')
    sns.lineplot(x='Year', y='AvgReturn', data=combined_data, hue='Window', palette='Blues')
    plt.legend(loc='best')
    graph.yaxis.set_major_formatter(PercentFormatter(1))
    sns.despine()

