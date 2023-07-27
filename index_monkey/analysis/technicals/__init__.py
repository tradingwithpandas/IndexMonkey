import talib
import pandas as pd
import yfinance as yf


def get_SMA(px_data, px_col, timeperiod):
    sma_fn = talib.abstract.Function('SMA')
    ticker_sma = sma_fn(px_data, timeperiod=timeperiod, price=px_col)
    ticker_sma = ticker_sma.rename(f'{timeperiod}DSMA')
    return ticker_sma


def get_EMA(px_data, px_col, timeperiod):
    ema_fn = talib.abstract.Function('EMA')
    ticker_ema = ema_fn(px_data, timeperiod=timeperiod, price=px_col)
    ticker_ema = ticker_ema.rename(f'{timeperiod}DEMA')
    return ticker_ema


def get_BBANDS(px_data):
    upper, middle, lower = talib.BBANDS(px_data['Close'], matype=talib.MA_Type.T3)
    upper = upper.rename('upper_BBAND')
    middle = middle.rename('middle_BBAND')
    lower = lower.rename('lower_BBAND')
    bbands = pd.merge(upper, middle, left_index=True, right_index=True)
    bbands = pd.merge(bbands, lower, left_index=True, right_index=True)
    return bbands


def get_px_with_SMA_and_BBANDS(ticker, period, ma_windows=None):
    ma_windows = ma_windows or [20, 50, 100, 200]
    px_hist = yf.Ticker(ticker).history(period=period)
    sma_20, sma_50, sma_100, sma_200 = [get_SMA(px_hist, 'Close', window) for window in ma_windows]

    bbands = get_BBANDS(px_hist)

    rsi = talib.RSI(px_hist['Close'], timeperiod=14).rename('RSI')

    px_and_technicals = px_hist.merge(sma_20, left_index=True, right_index=True)
    px_and_technicals = px_and_technicals.merge(sma_50, left_index=True, right_index=True)
    px_and_technicals = px_and_technicals.merge(sma_100, left_index=True, right_index=True)
    px_and_technicals = px_and_technicals.merge(sma_200, left_index=True, right_index=True)
    px_and_technicals = px_and_technicals.merge(bbands, left_index=True, right_index=True)
    px_and_technicals = px_and_technicals.merge(rsi, left_index=True, right_index=True)
    px_and_technicals = px_and_technicals.tz_localize(None)
    return px_and_technicals
