import datetime
from pandas.tseries.offsets import BDay


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
