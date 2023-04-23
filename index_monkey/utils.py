import datetime
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns


def get_first_biz_day_of_month(eff_date):
    # ToDo - See if you can handle missing dates based on exchange holidays
    first_biz_day_of_month = datetime.datetime(eff_date.year, eff_date.month, 1)
    if first_biz_day_of_month.month == 1:
        first_biz_day_of_month = datetime.datetime(eff_date.year, eff_date.month, 2)
        if first_biz_day_of_month.isoweekday() == 1 and first_biz_day_of_month.day != 4:
            first_biz_day_of_month = first_biz_day_of_month + datetime.timedelta(days=1)
    else:
        if first_biz_day_of_month.isoweekday() == 6:
            days_to_add = 2
        elif first_biz_day_of_month.isoweekday() == 7:
            days_to_add = 1
        else:
            days_to_add = 0
        first_biz_day_of_month = first_biz_day_of_month + datetime.timedelta(days=days_to_add)

    return first_biz_day_of_month


def check_valid_month(month):
    if month is not None and month < 1 or month > 12:
        raise ValueError(f'Month should be between 1 and 12. You passed {month}')


def split_list(full_list, split_size):
    split_lists = []
    for i in range(0, len(full_list), split_size):
        split_lists.append(full_list[i:i+split_size])
    return split_lists


def daterange(start_date, end_date, ignore_weekends=False):
    eff_date = start_date
    while eff_date <= end_date:
        if eff_date.isoweekday() not in (6, 7):
            yield eff_date
        eff_date = eff_date + datetime.timedelta(days=1)


DAY_AGO_BIZ_DAYS = -1
WEEK_AGO_BIZ_DAYS = -5
MONTH_AGO_BIZ_DAYS = -20


def get_date_from_n_days_ago(eff_date, n_days, biz_day_mode=True):
    if biz_day_mode:
        new_date = (eff_date + BDay(n_days)).to_pydatetime().date()
    else:
        new_date = eff_date + datetime.timedelta(days=n_days)
    return new_date


def day_ago(eff_date, biz_day_mode=True):
    return get_date_from_n_days_ago(eff_date, DAY_AGO_BIZ_DAYS, biz_day_mode=biz_day_mode)


def week_ago(eff_date, biz_day_mode=True):
    return get_date_from_n_days_ago(eff_date, WEEK_AGO_BIZ_DAYS, biz_day_mode=biz_day_mode)


def month_ago(eff_date, biz_day_mode=True):
    return get_date_from_n_days_ago(eff_date, MONTH_AGO_BIZ_DAYS, biz_day_mode=biz_day_mode)


def parse_date(date_str, date_format='%Y-%m-%d'):
    try:
        parsed_date = datetime.datetime.strptime(date_str, date_format).date()
    except ValueError:
        parsed_date = None
    return parsed_date


def multiline_chart(data_df,
                    x_col,
                    y1_col,
                    y1_hue_col=None,
                    y1_hue_filter=None,
                    y2_col=None,
                    y2_hue_col=None,
                    y2_hue_filter=None,
                    x_label=None,
                    x_lim=None,
                    x_formatter=None,
                    x_custom_lines=None,
                    y1_label=None,
                    y1_lim=None,
                    y1_formatter=None,
                    y1_hue_palette=None,
                    y1_hue_sizes=None,
                    y1_custom_lines=None,
                    y2_label=None,
                    y2_lim=None,
                    y2_formatter=None,
                    y2_hue_palette=None,
                    y2_hue_sizes=None,
                    y2_custom_lines=None,
                    fontsize=12,
                    legend_override=None,
                    legend_addendum=None,
                    legend_fontsize=12,
                    legend_loc='best',
                    figsize=(16, 8),
                    title=None,
                    title_fontsize=14,
                    add_watermark=False,
                    watermark_txt='© Pandas Trader',
                    watermark_args=None,
                    save_path=None
                    ):
    '''
    Convenience function for multiline and dual-y-axis charts. Uses seaborn and matplotlib.
    :param data_df: Data that needs to be charted
    :param x_col: column name in data_df to use for X axis
    :param y1_col: column name in data_df to use for the left Y axis
    :param y1_hue_col: column name in data_df to use for the hue argument on the left Y axis
    :param y1_hue_filter: hue variables to show on the left Y axis
    :param y2_col: column name in data_df to use for the right Y axis
    :param y2_hue_col: column name in data_df to use for the hue argument on the right Y axis
    :param y2_hue_filter: hue variables to show on the right Y axis
    :param x_label: X axis label on the chart
    :param x_lim: tuple indicating the upper and lower bound of the X axis on the chart
    :param x_formatter: matplotlib formatter for X axis
    :param x_custom_lines: list of tuples which contain the position and kwargs to pass to the axvline call
    :param y1_label: left Y axis label on the chart
    :param y1_lim: tuple indicating the upper and lower bound of the left Y axis on the chart
    :param y1_formatter: matplotlib formatter for left Y axis
    :param y1_hue_palette: dict with keys of values found under the hue_col and values of corresponding matplotlib
    colors for the left Y axis
    :param y1_hue_sizes: dict with keys of values found under the hue_col and values of corresponding linewidths for the
    left Y axis
    :param y1_custom_lines: list of tuples which contain the position and kwargs to pass to the axhline call on the left
    Y axis
    :param y2_label: Right Y axis label on the chart
    :param y2_lim: tuple indicating the upper and lower bound of the right Y axis on the chart
    :param y2_formatter: matplotlib formatter for right Y axis
    :param y2_hue_palette: dict with keys of values found under the hue_col and values of corresponding matplotlib
    colors for the right Y axis
    :param y2_hue_sizes: dict with keys of values found under the hue_col and values of corresponding linewidths for the
    right Y axis
    :param y2_custom_lines: list of tuples which contain the position and kwargs to pass to the axhline call on the
    right Y axis
    :param fontsize: Currently unused
    :param legend_override: dict of label: matplotlib.patches.Patch() objects to denote each line on the chart. This
    will override the existing legend
    :param legend_addendum: dict of label: matplotlib.patches.Patch() objects to denote each line on the chart. This
    will append the existing legend
    :param legend_fontsize: Font size to use in the legend
    :param legend_loc: One of the following -  'best', 'upper right', 'upper left', 'lower left', 'lower right',
    'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
    :param figsize: Tuple indicating width and height of chart
    :param title: Title to display on chart
    :param title_fontsize: Font size of title to display on chart
    :param add_watermark: bool to indicate if watermark is required on the chart
    :param watermark_txt: str to indicate watermark txt
    :param watermark_args: ax.text kwargs to override watermark params. Defaults listed below.
        {'ha': 'center', 'va': 'center', 'alpha': 0.18, 'fontsize': 90, 'color': 'green'}
    :param save_path: str file path of where to save the chart
    :return:
    '''
    fig, ax = plt.subplots(figsize=figsize)
    filtered_data_df = data_df[data_df[y1_hue_col].isin(y1_hue_filter)]
    sns.lineplot(data=filtered_data_df, x=x_col, y=y1_col, hue=y1_hue_col, palette=y1_hue_palette,
                 sizes=y1_hue_sizes)
    ax.set(xlabel=x_label, ylabel=y1_label, xlim=x_lim, ylim=y1_lim)

    x_custom_lines = x_custom_lines or []
    for position, cust_line_kwargs in x_custom_lines:
        ax.axvline(position, **cust_line_kwargs)

    y1_custom_lines = y1_custom_lines or []
    for position, cust_line_kwargs in y1_custom_lines:
        ax.axhline(position, **cust_line_kwargs)

    if x_formatter:
        ax.xaxis.set_major_formatter(x_formatter)
    if y1_formatter:
        ax.xaxis.set_major_formatter(y1_formatter)
    if y2_col:
        ax2 = ax.twinx()
        filtered_data_df = data_df[data_df[y2_hue_col].isin(y2_hue_filter)]
        sns.lineplot(data=filtered_data_df, x=x_col, y=y2_col, hue=y2_hue_col, palette=y2_hue_palette,
                     sizes=y2_hue_sizes)
        ax2.set(ylabel=y2_label, ylim=y2_lim)

        y2_custom_lines = y2_custom_lines or []
        for position, cust_line_kwargs in y2_custom_lines:
            ax2.axhline(position, **cust_line_kwargs)

        if y2_formatter:
            ax2.xaxis.set_major_formatter(y2_formatter)
    else:
        ax2 = None

    handles, labels = ax.get_legend_handles_labels()
    if legend_override:
        handles = list(legend_override.values())
        labels = list(legend_override.keys())

    if legend_addendum:
        handles, labels = ax.get_handles_labels()
        handles.extend(list(legend_override.values()))
        labels.extend(list(legend_override.keys()))

    ax.legend(handles, labels, fontsize=legend_fontsize, loc=legend_loc)
    if ax2:
        ax2.get_legend().remove()

    if add_watermark:
        watermark_args = watermark_args or {}
        if 'ha' not in watermark_args:
            watermark_args['ha'] = 'center'
        if 'va' not in watermark_args:
            watermark_args['va'] = 'center'
        if 'alpha' not in watermark_args:
            watermark_args['alpha'] = 0.18
        if 'fontsize' not in watermark_args:
            watermark_args['fontsize'] = 90
        if 'color' not in watermark_args:
            watermark_args['color'] = 'green'

        ax.text(0.5, 0.5, watermark_txt, transform=ax.transAxes, **watermark_args)

    plt.title(title, fontsize=title_fontsize)

    # max_red_less_dp = max(tdf['Dirty Price'].values)
    # min_red_less_dp = min(tdf['Redemption Payment'].values)
    # ax.fill_between(
    #     tdf['Date'],
    #     [max_red_less_dp] * len(tdf),
    #     [min_red_less_dp] * len(tdf),
    #     where=tdf['Redemption less Dirty Px'] > 0,
    #     facecolor='green',
    #     alpha=0.25)
    if save_path:
        plt.savefig(save_path)
    plt.show()
