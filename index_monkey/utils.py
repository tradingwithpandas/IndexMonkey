
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
    if month < 1 or month > 12:
        raise ValueError(f'Month should be between 1 and 12. You passed {month}')


def split_list(full_list, split_size):
    split_lists = []
    for i in range(0, len(full_list), split_size):
        split_lists.append(full_list[i:i+split_size])
    return split_lists
