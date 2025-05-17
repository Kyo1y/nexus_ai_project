from dateutil.relativedelta import relativedelta

import datetime
import logging

logger = logging.getLogger("logger")

date_format = '%Y-%m-%dT%H:%M:%SZ'
date_unit_key_list = ['days', 'months', 'years']

def get_previous_date(unit, value):
    if unit not in date_unit_key_list:
        raise Exception("unknown time unit key")
        
    if not isinstance(value, int):
        raise Exception("period value is not an integer")

    if unit == 'days':
        period_val = value + 1
        previous_date = (datetime.datetime.today() - relativedelta(days=period_val))
    elif unit == 'months':
        period_val = value + 3
        previous_date = (get_first_day_of_current_month() - relativedelta(months=period_val))
    elif unit == 'years':
        period_val = value + 1
        previous_date = (datetime.datetime.today() - relativedelta(years=period_val))
        
    return previous_date

def get_current_date():
    return datetime.datetime.now().strftime(date_format)

def get_first_day_of_current_month():
    """
    Returns the first day of the current month as a datetime.date object.
    """
    today = datetime.date.today()
    first_day_of_current_month = datetime.date(today.year, today.month, 1)
    return first_day_of_current_month