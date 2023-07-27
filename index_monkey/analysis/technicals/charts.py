import matplotlib.pyplot as plt
import pandas as pd
from index_monkey.chart_utils import multiline_chart_subplot
from index_monkey.analysis.technicals import get_px_with_SMA_and_BBANDS


def plot_px_with_technicals(ticker, period):
    px = get_px_with_SMA_and_BBANDS(ticker, period).reset_index()
    px_melted = pd.melt(px, ['Date'], ['Close', '20DSMA', '50DSMA', '100DSMA', '200DSMA', 'upper_BBAND', 'middle_BBAND', 'lower_BBAND', 'RSI'])
    plt.style.use('dark_background')
    sma_px_subplot_args = {
        'x_col': 'Date',
        'y1_col': 'value',
        'y1_hue_col': 'variable',
        'y1_hue_filter': ['Close', '20DSMA', '50DSMA', '100DSMA', '200DSMA'],
        'y1_hue_palette': {'Close': 'orange', '20DSMA': 'red', '50DSMA': 'cyan', '100DSMA': 'green', '200DSMA': 'white'},
        'add_watermark': True,
        'title': f'{ticker} Close vs 20, 50, 100, 200 SMAs)',
    }
    bband_subplot_args = {
        'x_col': 'Date',
        'y1_col': 'value',
        'y1_hue_col': 'variable',
        'y1_hue_filter': ['upper_BBAND', 'middle_BBAND', 'lower_BBAND'],
        'y1_hue_palette': {'upper_BBAND': 'red', 'middle_BBAND': 'white', 'lower_BBAND': 'red'},
        'add_watermark': True,
        'title': f'{ticker} Bollinger Bands',
    }
    rsi_subplot_args = {
        'x_col': 'Date',
        'y1_col': 'value',
        'y1_hue_col': 'variable',
        'y1_hue_filter': ['RSI'],
        'y1_hue_palette': {'RSI': 'white'},
        'add_watermark': True,
        'title': f'{ticker} RSI',
        'y1_custom_lines': [(80, {'color': 'red'}), (20, {'color': 'red'})],
        'y1_lim': (0, 100)
    }
    multiline_chart_subplot(
        px_melted,
        rows=3,
        subplot_args=[sma_px_subplot_args, bband_subplot_args, rsi_subplot_args],
        height_ratios=(1, 0.25, 0.25),
        figsize=(25, 16),
    )