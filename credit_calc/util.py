import calendar
import datetime

DATE_FORMAT = "%d.%m.%Y"


class Error(Exception):
    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(
            error.format(*args, **kwargs) if args or kwargs else error)

class InvalidDateError(Error):
    def __init__(self, date):
        super(InvalidDateError, self).__init__("Invalid date: {}.", date)


def get_date(date):
    if isinstance(date, datetime.date):
        return date

    try:
        return datetime.datetime.strptime(date, DATE_FORMAT).date()
    except ValueError:
        raise InvalidDateError(date)


def format_date(date):
    return date.strftime(DATE_FORMAT)


def year_days(year):
    return 366 if calendar.isleap(year) else 365
