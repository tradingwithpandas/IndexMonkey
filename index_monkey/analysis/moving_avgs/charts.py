from index_monkey.analysis.moving_avgs import get_pct_above_ma
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def chart_pct_above_sma(index_name, start_date, end_date, index_start_date=None, index_end_date=None,
                        timeperiods=(50, 200), use_latest_index_weighting=False):
    spy_sector_smas = get_pct_above_ma(index_name,
                                       start_date,
                                       end_date,
                                       timeperiods=timeperiods,
                                       use_latest_index_weighting=use_latest_index_weighting,
                                       sector_lvl=False)
    col_rename_map = {f'PctAbove{period}DSMA': f'{period}DSMA' for period in timeperiods}
    spy_sector_smas = spy_sector_smas.rename(columns=col_rename_map)
    spy_sector_smas = pd.melt(spy_sector_smas, ['pdate'], col_rename_map.values())
    spy_sector_smas = spy_sector_smas.rename(columns={'value': '%', 'variable': 'Moving Average'})

    idx = yf.Ticker(index_name)
    idx_px = idx.history(start=start_date, end=end_date)
    idx_px = idx_px.reset_index()
    idx_px = idx_px.rename(columns={'Close': 'Price'})
    idx_px = idx_px[['Date', 'Price']]

    fig, ax = plt.subplots(figsize=(20, 12))
    fig.autofmt_xdate()
    timeperiods_in_title = ', '.join([f'{period}D' for period in timeperiods])
    chart_title = f'SPY with % of Stocks above {timeperiods_in_title} SMA by Sector'
    ax.set_title(chart_title)
    graph = sns.lineplot(x='Date', y='Price', data=idx_px, color='black')
    graph2 = graph.twinx()
    graph2 = sns.lineplot(x='pdate', y='%', hue='Moving Average', data=spy_sector_smas)
    plt.legend(loc='best')
    graph2.yaxis.set_major_formatter(PercentFormatter(1))
