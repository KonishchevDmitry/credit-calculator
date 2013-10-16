import calendar

from collections import namedtuple
from datetime import datetime as Date
from decimal import Decimal

DATE_FORMAT = "%d.%m.%Y"


class Error(Exception):
    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(
            error.format(*args, **kwargs) if args or kwargs else error)

class LogicalError(Error):
    def __init__(self, date):
        super(LogicalError, self).__init__("Logical error.")

class InvalidDateError(Error):
    def __init__(self, date):
        super(InvalidDateError, self).__init__("Invalid date: {}.", date)

class InvalidDateRangeError(Error):
    def __init__(self, start, end):
        super(InvalidDateRangeError, self).__init__("Invalid date range error: {} - {}.", start, end)


MonthInterest = namedtuple("MonthInterest", ("date", "interest"))


def _iter_months(start_date_string, end_date_string):
    date = _parse_date(start_date_string)
    end_date = _parse_date(end_date_string)
    start_day = date.day

    yield date

    while date != end_date:
        if date > end_date:
            raise InvalidDateRangeError(start_date_string, end_date_string)

        if date.month == 12:
            year = date.year + 1
            month = 1
        else:
            year = date.year
            month = date.month + 1

        day = start_day

        while True:
            try:
                date = Date(year, month, day)
            except ValueError:
                if day < 28:
                    raise LogicalError()
                day -= 1
            else:
                break

        yield date


def _iter_month_interest(start_date, end_date, year_interest):
    year_interest = Decimal(year_interest) / 100

    prev = None
    for cur in _iter_months(start_date, end_date):
        if prev is None:
            prev = cur
            continue

        if cur.year == prev.year:
            interest = year_interest / _year_days(cur.year) * (cur - prev).days
        else:
            assert cur.month == 1
            assert prev.month == 12

            prev_days = (Date(prev.year, prev.month, 31) - prev).days
            cur_days = (cur - Date(cur.year, cur.month, 1)).days + 1
            assert prev_days + cur_days == (cur - prev).days

            interest = (
                year_interest / _year_days(prev.year) * prev_days +
                year_interest / _year_days(cur.year) * cur_days)

        yield MonthInterest(cur, interest)
        prev = cur


def _parse_date(string):
    try:
        return Date.strptime(string, DATE_FORMAT)
    except ValueError:
        raise InvalidDateError(string)

def _year_days(year):
    return 366 if calendar.isleap(year) else 365
