import calendar
from datetime import datetime as Date

DATE_FORMAT = "%d.%m.%Y"


class Error(Exception):
    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(
            error.format(*args, **kwargs) if args or kwargs else error)

class InvalidDateError(Error):
    def __init__(self, date):
        super(InvalidDateError, self).__init__("Invalid date: {}.", date)


def get_date(date):
    if isinstance(date, Date):
        return date

    try:
        return Date.strptime(date, DATE_FORMAT)
    except ValueError:
        raise InvalidDateError(date)


def format_date(date):
    return date.strftime(DATE_FORMAT)


def year_days(year):
    return 366 if calendar.isleap(year) else 365
