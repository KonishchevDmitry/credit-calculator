import pytest

from decimal import Decimal
from datetime import datetime as Date

from credit_calc import MonthInterest
from credit_calc import InvalidDateError, InvalidDateRangeError
from credit_calc import _iter_months, _iter_month_interest, _parse_date


def test_parse_date():
    assert _parse_date("13.03.2013") == Date(2013, 3, 13)

def test_parse_date_invalid():
    with pytest.raises(InvalidDateError):
        _parse_date("31.02.2013")


def test_iter_months_simple():
    assert list(_iter_months("15.03.2013", "15.05.2013")) == [
        _parse_date("15.03.2013"), _parse_date("15.04.2013"), _parse_date("15.05.2013") ]

def test_iter_months_from_year_to_year():
    assert list(_iter_months("15.11.2013", "15.02.2014")) == [
        _parse_date("15.11.2013"), _parse_date("15.12.2013"),
        _parse_date("15.01.2014"), _parse_date("15.02.2014") ]

def test_iter_months_invalid_date():
    with pytest.raises(InvalidDateError):
        list(_iter_months("31.02.2013", "31.05.2013"))

def test_iter_months_invalid_range():
    with pytest.raises(InvalidDateRangeError):
        list(_iter_months("15.03.2013", "17.05.2013"))

    with pytest.raises(InvalidDateRangeError):
        list(_iter_months("15.03.2013", "17.03.2012"))

    with pytest.raises(InvalidDateRangeError):
        list(_iter_months("15.03.2013", "17.05.2012"))

def test_iter_months_with_non_existing_days_in_months():
    assert list(_iter_months("31.12.2012", "30.04.2013")) == [
        _parse_date("31.12.2012"), _parse_date("31.01.2013"),
        _parse_date("28.02.2013"), _parse_date("31.03.2013"),
        _parse_date("30.04.2013") ]


def test_iter_month_interest():
    assert list(_iter_month_interest("31.12.2012", "28.02.2013", str(365 * 2))) == [
        MonthInterest(Date(2013, 1, 31), Decimal("0.62")),
        MonthInterest(Date(2013, 2, 28), Decimal("0.56")) ]
