import datetime
from .utils import wrap_list
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns


def _fill_between_line_chart(axis, data_df, fill_between_args):
    pass



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
                    y1_fill_between_args=None,
                    y2_label=None,
                    y2_lim=None,
                    y2_formatter=None,
                    y2_hue_palette=None,
                    y2_hue_sizes=None,
                    y2_custom_lines=None,
                    y2_fill_between_args=None,
                    fontsize=12,
                    ax=None,
                    legend_override=None,
                    legend_addendum=None,
                    legend_fontsize=12,
                    legend_loc='best',
                    figsize=(16, 8),
                    title=None,
                    title_fontdict=None,
                    add_watermark=False,
                    watermark_txt='© Pandas Trader',
                    watermark_args=None,
                    source=None,
                    save_path=None
                    ):
    """
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
    :param title_fontdict: Font formatting params like fontsize, fontweight, color, verticalalignment,
    horizontalalignment
    :param add_watermark: bool to indicate if watermark is required on the chart
    :param watermark_txt: str to indicate watermark txt
    :param watermark_args: ax.text kwargs to override watermark params. Defaults listed below.
        {'ha': 'center', 'va': 'center', 'alpha': 0.18, 'fontsize': 90, 'color': 'green'}
    :param source: String at the bottom of the chart to provide data sources or other accreditations
    :param save_path: str file path of where to save the chart
    :return:
    """
    if not ax:
        fig, ax = plt.subplots(figsize=figsize)
    filtered_data_df = data_df[data_df[y1_hue_col].isin(y1_hue_filter)]
    sns.lineplot(data=filtered_data_df, x=x_col, y=y1_col, hue=y1_hue_col, palette=y1_hue_palette,
                 sizes=y1_hue_sizes, ax=ax)
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
        ax.yaxis.set_major_formatter(y1_formatter)
    if y2_col:
        ax2 = ax.twinx()
        filtered_data_df = data_df[data_df[y2_hue_col].isin(y2_hue_filter)]
        sns.lineplot(data=filtered_data_df, x=x_col, y=y2_col, hue=y2_hue_col, palette=y2_hue_palette,
                     sizes=y2_hue_sizes, ax=ax2)
        ax2.set(ylabel=y2_label, ylim=y2_lim)

        y2_custom_lines = y2_custom_lines or []
        for position, cust_line_kwargs in y2_custom_lines:
            ax2.axhline(position, **cust_line_kwargs)

        if y2_formatter:
            ax2.yaxis.set_major_formatter(y2_formatter)
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
        ax2_legend = ax2.get_legend()
        if ax2_legend:
            ax2_legend.remove()

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
    if source:
        ax.text(x=0.5, y=-0.12, s=source, fontsize=10, alpha=0.75, ha='center', va='bottom',
                transform=ax.transAxes)
    ax.set_title(title, fontdict=title_fontdict)

    # if y1_fill_between_args:
    #     y1_fill_between_args = wrap_list(y1_fill_between_args)
    #     for arg in y1_fill_between_args:

    # max_red_less_dp = max(tdf['Dirty Price'].values)
    # min_red_less_dp = min(tdf['Redemption Payment'].values)
    # ax.fill_between(
    #     tdf['Date'],
    #     [max_red_less_dp] * len(tdf),
    #     [min_red_less_dp] * len(tdf),
    #     where=tdf['Redemption less Dirty Px'] > 0,
    #     facecolor='green',
    #     alpha=0.25)
    # if save_path:
    #     plt.savefig(save_path)
    # plt.show()


def multiline_chart_subplot(data_df,
                            rows=1,
                            cols=1,
                            subplot_args=None,
                            height_ratios=None,
                            width_ratios=None,
                            figsize=(16, 8),
                            save_path=None
                            ):
    """
    Convenience function for multiline and dual-y-axis charts. Uses seaborn and matplotlib.
    :return:
    """
    fig, axs = plt.subplots(rows, cols, figsize=figsize, width_ratios=width_ratios, height_ratios=height_ratios)
    axs = wrap_list(axs)
    subplot_args = wrap_list(subplot_args)
    if len(axs) != len(subplot_args):
        raise Exception(f'Subplot args don\'t match the number of axes in your subplot. {len(subplot_args)} vs {len(axs)}')
    for ax, subplot_arg in zip(axs, subplot_args):
        multiline_chart(data_df, ax=ax, **subplot_arg)
    plt.show()
    if save_path:
        plt.savefig(save_path)
