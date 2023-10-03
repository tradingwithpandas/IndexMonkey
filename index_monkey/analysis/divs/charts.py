from index_monkey.analysis.divs import get_total_return
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from jinja2 import Template


def get_bal_return_and_cagr_string(bal, start_bal, bal_date, start_bal_date):
    bal_str = f'{bal:,.0f}'
    bal_return_str = f'{(bal / start_bal) - 1:,.2%}'
    bal_date_minus_start_period = (bal_date.year - start_bal_date.year) or 1
    bal_cagr = ((bal / start_bal) ** (1 / bal_date_minus_start_period)) - 1
    bal_cagr_str = f'{bal_cagr:,.2%}'
    return bal_str, bal_return_str, bal_cagr_str


def _annotate_total_return_chart(div_df, ccy, axis):
    start_date = div_df.iloc[0]['Date']
    start_bal = div_df.iloc[0]['mv']
    start_bal_str = f'{start_bal:,.0f}'

    max_bal = max(div_df['mv'])
    max_bal_date = div_df[div_df['mv'] == max_bal].iloc[0]['Date']
    max_bal_str, max_bal_return, max_bal_cagr_str = get_bal_return_and_cagr_string(max_bal, start_bal, max_bal_date, start_date)

    end_date = div_df.iloc[-1]['Date']
    end_bal = div_df.iloc[-1]['mv']
    end_bal_str, end_bal_return, end_bal_cagr_str = get_bal_return_and_cagr_string(end_bal, start_bal, end_date, start_date)

    annotation_points = [(start_date, start_bal, start_bal_str, None, None),
                         (max_bal_date, max_bal, max_bal_str, max_bal_return, max_bal_cagr_str),
                         (end_date, end_bal, end_bal_str, end_bal_return, end_bal_cagr_str)]
    for dt, bal, bal_str, bal_return, cagr in annotation_points:
        base_annotation = '{{bal_str}} {{ccy}}'
        bal_return_annotation = '{% if bal_return %} {{ bal_return }} {% endif %}'
        cagr_annotation = '{% if cagr %} {{ cagr }} CAGR {% endif %}'
        annotation_jinja_str = f'{base_annotation} {bal_return_annotation} {cagr_annotation}'
        annotation = Template(annotation_jinja_str).render(bal_str=bal_str, ccy=ccy, bal_return=bal_return, cagr=cagr)
        axis.annotate(annotation, (dt, bal), fontsize=12, xytext=(-70, 30), textcoords='offset points',
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
