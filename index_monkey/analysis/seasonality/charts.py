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
    ticker_returns['AvgReturn'] = ticker_returns['Return%'].mean()
    fig, ax = plt.subplots(figsize=(10, 8))
    month1_name = MONTH_MAP.get(month1)
    month2_name = MONTH_MAP.get(month2)
    ax.set_title(f'{ticker} Seasonal Performance in {month1_name}-{month2_name}')
    fig.autofmt_xdate()
    graph = sns.barplot(x='Year', y='Return%', data=ticker_returns, palette='Blues')
    sns.lineplot(x='Year', y='AvgReturn', data=ticker_returns)
    graph.yaxis.set_major_formatter(PercentFormatter(1))
    sns.despine()
