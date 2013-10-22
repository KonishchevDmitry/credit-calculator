import functools

from collections import namedtuple
from datetime import datetime as Date
from decimal import Decimal

from credit_calc.util import Error, InvalidDateError
from credit_calc.util import get_date, format_date, year_days


class InvalidDateRangeError(Error):
    def __init__(self, start, end):
        super(InvalidDateRangeError, self).__init__("Invalid date range error: {} - {}.", start, end)

class InvalidPaymentDateError(Error):
    def __init__(self, *args, **kwargs):
        super(InvalidPaymentDateError, self).__init__(*args, **kwargs)

class InvalidPaymentError(Error):
    def __init__(self, *args, **kwargs):
        super(InvalidPaymentError, self).__init__(*args, **kwargs)

Credit = namedtuple("Credit", ("start_date", "end_date", "amount", "current_amount", "interest", "month_pay", "schedule"))
Payment = namedtuple("Payment", ("date", "credit_pay", "interest_pay", "month_pay", "credit"))
MonthInterest = namedtuple("MonthInterest", ("date", "interest"))



def get_credit_info(info_date, start_date, end_date, amount, interest, payments={}):
    info_date = get_date(info_date)
    start_date = get_date(start_date)
    end_date = get_date(end_date)
    amount = Decimal(amount)
    interest = Decimal(interest)

    payment_schedule = _calculate(start_date, end_date, amount, interest, payments)

    month_pay = None

    if info_date <= end_date:
        prev_date = start_date
        current_amount = amount

        for payment in payment_schedule:
            if not (payment.date <= info_date or prev_date < info_date):
                break

            if payment.date <= info_date:
                current_amount = payment.credit

            month_pay = payment.month_pay
            prev_date = payment.date
    else:
        current_amount = 0

    return Credit(start_date, end_date, amount, current_amount, interest, month_pay, payment_schedule)


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
    date = get_date(start_date_string)
    end_date = get_date(end_date_string)
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
            day_interest = year_interest / year_days(cur.year)
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

            day_interest = year_interest / year_days(cur.year)
            interest += day_interest * cur_days

        yield MonthInterest(cur, interest)
        prev = cur


def _count_months(start_date, end_date):
    return functools.reduce(lambda count, date: count + 1,
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


def _calculate(start_date, end_date, credit, interest, payments={}):
    start_date = get_date(start_date)
    end_date = get_date(end_date)
    credit = Decimal(credit)

    payments = { get_date(date): Decimal(payment)
        for date, payment in payments.items() }

    schedule = []
    prev_date = start_date
    cur_month_pay = month_pay = None
    for date, month_interest in _iter_month_interest(start_date, end_date, interest):
        if month_pay is None or cur_month_pay != month_pay:
            month_pay = _get_month_pay(prev_date, end_date, credit, interest)

        cur_month_pay = payments.pop(date, month_pay)
        if cur_month_pay < month_pay:
            raise InvalidPaymentError(
                "Invalid payment for {}.", format_date(date))

        interest_pay = _round_payment(credit * month_interest)
        credit_pay = cur_month_pay - interest_pay
        credit -= credit_pay

        schedule.append(Payment(
            date, credit_pay, interest_pay, cur_month_pay, credit))

        prev_date = date

    if payments:
        raise InvalidPaymentDateError("Invalid payment date: {}.",
            format_date(payments.popitem()[0]))

    if credit:
        payment = schedule[-1]
        schedule[-1] = Payment(
            payment.date, payment.credit_pay + credit,
            interest_pay, payment.month_pay + credit, 0)

    return schedule
