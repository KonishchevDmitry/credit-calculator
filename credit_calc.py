import calendar

from collections import namedtuple
from datetime import datetime as Date
from decimal import Decimal

DATE_FORMAT = "%d.%m.%Y"


class Error(Exception):
    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(
            error.format(*args, **kwargs) if args or kwargs else error)

#class LogicalError(Error):
#    def __init__(self, date):
#        super(LogicalError, self).__init__("Logical error.")

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

        date = _nearest_valid_date(year, month, start_day)

        yield date


def _iter_month_interest(start_date, end_date, year_interest):
    year_interest = Decimal(year_interest) / 100

    def get_credit_year(start):
        end = _nearest_valid_date(start.year + 1, start.month, start.day)
        year_days = (end - start).days
        assert year_days in (365, 366)
        day_interest = year_interest / year_days
        return end, day_interest

    credit_year_end, day_interest = get_credit_year(_parse_date(start_date))

    prev = None
    for cur in _iter_months(start_date, end_date):
        if prev is None:
            prev = cur
            continue

        assert cur <= credit_year_end
        yield MonthInterest(cur, day_interest * (cur - prev).days)

        if cur == credit_year_end:
            credit_year_end, day_interest = get_credit_year(credit_year_end)

        prev = cur


def _nearest_valid_date(year, month, day):
    while True:
        try:
            return Date(year, month, day)
        except ValueError:
            if day < 28:
                raise InvalidDateError("{:02d}.{:02d}.{:04d}".format(day, month, year))
            day -= 1


def _parse_date(string):
    try:
        return Date.strptime(string, DATE_FORMAT)
    except ValueError:
        raise InvalidDateError(string)


def _year_days(year):
    return 366 if calendar.isleap(year) else 365
