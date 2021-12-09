import yfinance as yf
import datetime
from index_monkey.utils import check_valid_month, get_first_biz_day_of_month

def get_historic_specific_month_performance(ticker, month1, month2):
    # Check that a valid month has been passed for the comparison
    check_valid_month(month1)
    check_valid_month(month2)

    yf_ticker = yf.Ticker(ticker)
    px_hist = yf_ticker.history(period='max')
    px_hist = px_hist.reset_index()

    # Only keep px history for the 2 months passed in and remove all weekends
    px_hist = px_hist[px_hist['Date'].dt.month.isin((month1, month2))]
    px_hist = px_hist[~px_hist['Date'].dt.dayofweek.isin((5, 6))]

    # Find first day of each month that's left in the dataset
    px_hist['FirstBizDayOfMonth'] = px_hist['Date'].apply(get_first_biz_day_of_month)
    px_hist = px_hist[px_hist['Date'] == px_hist['FirstBizDayOfMonth']]

    px_hist = px_hist[['Date', 'Close']]
    px_hist = px_hist.sort_values(['Date'])

    # Calculate Returns
    px_hist['PrevClose'] = px_hist['Close'].shift(1)
    px_hist['MonthlyDiff'] = px_hist['Close'] - px_hist['PrevClose']
    px_hist = px_hist[px_hist['Date'].dt.month == month2]
    px_hist['Return%'] = px_hist['MonthlyDiff'] / px_hist['PrevClose']
    return px_hist

