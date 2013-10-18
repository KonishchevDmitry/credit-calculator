import calendar

from collections import namedtuple
from datetime import datetime as Date
from decimal import Decimal


class Error(Exception):
    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(
            error.format(*args, **kwargs) if args or kwargs else error)

class InvalidDateError(Error):
    def __init__(self, date):
        super(InvalidDateError, self).__init__("Invalid date: {}.", date)

class InvalidDateRangeError(Error):
    def __init__(self, start, end):
        super(InvalidDateRangeError, self).__init__("Invalid date range error: {} - {}.", start, end)

MonthInterest = namedtuple("MonthInterest", ("date", "interest"))



def _year_days(year):
    return 366 if calendar.isleap(year) else 365


def _parse_date(string):
    try:
        return Date.strptime(string, "%d.%m.%Y")
    except ValueError:
        raise InvalidDateError(string)


def _nearest_valid_date(year, month, day):
    date_string = "{:02d}.{:02d}.{:04d}".format(day, month, year)

    if year < 1 or month < 1 or month > 12 or day < 1 or day > 31:
        raise InvalidDateError(date_string)

    while True:
        try:
            return Date(year, month, day)
        except ValueError:
            if day < 28:
                raise InvalidDateError(date_string)
            day -= 1



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

    prev = None
    day_interest = None
    for cur in _iter_months(start_date, end_date):
        if prev is None:
            day_interest = year_interest / _year_days(cur.year)
            prev = cur
            continue

        if cur.year == prev.year:
            interest = day_interest * (cur - prev).days
        else:
            assert prev.month == 12
            assert cur.month == 1

            prev_days = (Date(prev.year, prev.month, 31) - prev).days
            cur_days = (cur - Date(cur.year, cur.month, 1)).days + 1
            assert prev_days + cur_days == (cur - prev).days

            interest = day_interest * prev_days

            day_interest = year_interest / _year_days(cur.year)
            interest += day_interest * cur_days

        yield MonthInterest(cur, interest)
        prev = cur


def _count_months(start_date, end_date):
    return reduce(lambda count, date: count + 1,
        _iter_months(start_date, end_date), -1)



def _round_payment(payment):
    return payment.quantize(Decimal("1.00"))


def _get_month_pay(start_date, end_date, credit, interest):
    credit = Decimal(credit)
    months = _count_months(start_date, end_date)
    month_interest = Decimal(interest) / 12 / 100

    month_pay = credit * (month_interest * (1 + month_interest) ** months) \
        / ((1 + month_interest) ** months - 1)

    return _round_payment(month_pay)
