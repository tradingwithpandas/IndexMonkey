import yfinance as yf
import datetime
import pandas as pd


def _determine_buckets(start_value, end_value, num_buckets):
    bucket_size = (abs(start_value) + abs(end_value)) / num_buckets
    buckets = []
    prev_value = start_value
    for i in range(0, num_buckets):
        next_value = prev_value + bucket_size
        buckets.append((prev_value, next_value))
        prev_value = next_value
    buckets.append((end_value, end_value))
    return buckets


def _get_freq_str(row):
    return_str = f'{row.Return:.2%}'
    freq_count_str = f'{row.frequency:.2%} ({row.frequency_count or 0:.0f})'
    return f'{freq_count_str}\n{return_str}'


def _format_vol_histogram_df(ret_dist_df):
    ret_dist_df = ret_dist_df.reset_index()
    ret_dist_df = ret_dist_df.drop('index', axis=1)
    total_observations = ret_dist_df['frequency_count'].sum()
    ret_dist_df['frequency'] = ret_dist_df['frequency_count'] / total_observations
    ret_dist_df['Return'] = (ret_dist_df['bucket_start_val'] + ret_dist_df['bucket_end_val']) / 2
    ret_dist_df['freq_str'] = ret_dist_df.apply(_get_freq_str, axis=1)
    return ret_dist_df


def volatility_histogram_df(ticker: str,
                            return_window: str,
                            start_date: datetime.date = None,
                            end_date: datetime.date = None,
                            num_buckets: int = 10,
                            px_hist_override: pd.DataFrame = None):
    """
    Fetch a dataframe that calculates the volatility histogram dataframe for your desired timeframe over a
    date range which is optional
    :param ticker:          str ticker of the name whose volatility you wish to calculate
    :param return_window:   str denoting the return period over which to measure the volatility. This argument must
                            be a DateOffset, Timedelta or str
    :param start_date:      optional datetime.date param to indicate which date the price history starts from. If
                            both start_date and end_date are left as None, the function will try to fetch max
                            history from yfinance
    :param end_date:        optional datetime.date param to indicate which date the price history ends at. If
                            both start_date and end_date are left as None, the function will try to fetch max
                            history from yfinance
    :param num_buckets:     optional int param to indicate the number of rows the final output should be broken into.
                            Increase this param if you want to see a more granular view into the various return ranges
    :param px_hist_override:pd.DataFrame of price history to use as an alternative to pulling the data from yfinance.
                            This DataFrame should have a 'Date' index and a 'Close' column similar to price DataFrames
                            that come from yfinance
    :return:                a pandas DataFrame with Frequency and Return columns. These columns denote the number of
                            times (denoted in % terms in the Frequency column) the ticker returned various ranges of
                            returns (denoted in % terms in the Return column). The number of rows in the final output is
                            determined by the num_buckets param
    """
    yf_ticker = yf.Ticker(ticker)
    if start_date is None and end_date is None:
        px_hist_args = {'period': 'max'}
    else:
        px_hist_args = {'start': start_date, 'end': end_date}
    passed_valid_px_hist_override = px_hist_override is not None and not px_hist_override.empty
    px_hist = px_hist_override if passed_valid_px_hist_override else yf_ticker.history(**px_hist_args)
    px_hist['ticker'] = ticker
    px_hist = px_hist[['ticker', 'Close']]
    sampled_px_hist = px_hist.resample(return_window).first()
    sampled_px_hist['Return'] = sampled_px_hist['Close'].rolling(window=2).apply(
        lambda row: (row.iloc[-1] - row.iloc[0]) / row.iloc[0])
    sampled_px_hist = sampled_px_hist[~sampled_px_hist['Return'].isna()]
    min_return = sampled_px_hist['Return'].min()
    max_return = sampled_px_hist['Return'].max()
    return_buckets = _determine_buckets(min_return, max_return, num_buckets)

    return_distribution = None
    for start_val, end_val in return_buckets:
        if start_val != end_val:
            returns_in_bucket = sampled_px_hist[(sampled_px_hist['Return'] >= start_val) &
                                                (sampled_px_hist['Return'] < end_val)].copy()
        else:
            returns_in_bucket = sampled_px_hist[sampled_px_hist['Return'] == start_val].copy()

        if returns_in_bucket.empty:
            returns_in_bucket = pd.DataFrame([{'bucket_start_val': start_val, 'bucket_end_val': end_val,
                                               'frequency_count': 0}])
        else:
            returns_in_bucket.loc[:, 'bucket_start_val'] = start_val
            returns_in_bucket.loc[:, 'bucket_end_val'] = end_val or 'End of Range'
            returns_in_bucket = returns_in_bucket.groupby(['bucket_start_val', 'bucket_end_val']) \
                .agg({'Return': 'count'})
            returns_in_bucket = returns_in_bucket.reset_index()
            returns_in_bucket = returns_in_bucket.rename(columns={'Return': 'frequency_count'})
            returns_in_bucket = returns_in_bucket[['bucket_start_val', 'bucket_end_val', 'frequency_count']]
        if return_distribution is not None:
            return_distribution = pd.concat([return_distribution, returns_in_bucket])
        else:
            return_distribution = returns_in_bucket
    return_distribution = return_distribution[return_distribution['frequency_count'] != 0]
    return_distribution = _format_vol_histogram_df(return_distribution)
    return return_distribution
