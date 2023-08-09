from index_monkey.analysis.divs import get_total_return
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf


def _annotate_total_return_chart(div_df, ccy, axis):
    start_date = div_df.iloc[0]['Date']
    start_bal = div_df.iloc[0]['mv']
    end_date = div_df.iloc[-1]['Date']
    end_bal = div_df.iloc[-1]['mv']

    max_bal = max(div_df['mv'])
    max_bal_date = div_df[div_df['mv'] == max_bal].iloc[0]['Date']
    annotation_points = [(start_date, start_bal), (max_bal_date, max_bal), (end_date, end_bal)]
    for dt, bal in annotation_points:
        axis.annotate(f'{bal:,.0f} {ccy}', (dt, bal), fontsize=12, xytext=(-70, 30), textcoords='offset points',
                      arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=10"))


def chart_total_return(ticker, qty, period='10y'):
    ticker_div_df = get_total_return(ticker, qty, period)
    yft = yf.Ticker(ticker).get_info()
    plt.tight_layout()
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_title('Total Return {}'.format(ticker), fontsize=16)
    ax.set_xlabel('Date', fontsize=16)
    ax.set_ylabel('Market Value (# of Shares * Price)', fontsize=16)
    sns.lineplot(data=ticker_div_df.reset_index(level=0), x='Date', y='mv')
    ccy = yft.get('currency') or ' '
    _annotate_total_return_chart(ticker_div_df, ccy, ax)
    plt.show()
