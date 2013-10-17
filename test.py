import pytest

from decimal import Decimal
from datetime import datetime as Date

from credit_calc import MonthInterest
from credit_calc import InvalidDateError, InvalidDateRangeError
from credit_calc import _parse_date, _nearest_valid_date, _year_days
from credit_calc import _iter_months, _iter_month_interest, _count_months
from credit_calc import _round_payment, _get_month_pay


def test_year_days():
    _year_days(2012) == 366
    _year_days(2013) == 365


def test_parse_date():
    assert _parse_date("13.03.2013") == Date(2013, 3, 13)

def test_parse_date_invalid():
    with pytest.raises(InvalidDateError):
        _parse_date("31.02.2013")


def test_nearest_valid_date_valid():
    assert _nearest_valid_date(2013, 10, 13) == Date(2013, 10, 13)

def test_nearest_valid_date_invalid():
    with pytest.raises(InvalidDateError):
        assert _nearest_valid_date(2013, 2, 32)

    with pytest.raises(InvalidDateError):
        assert _nearest_valid_date(2013, 13, 1)

    with pytest.raises(InvalidDateError):
        assert _nearest_valid_date(0, 1, 1)

def test_nearest_valid_date_invalid_for_month():
    assert _nearest_valid_date(2013, 2, 31) == Date(2013, 2, 28)


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


def test_count_months():
    assert _count_months("31.12.2012", "30.04.2013") == 4


def test_round_payment():
    assert str(_round_payment(Decimal("100"))) == "100.00"
    assert str(_round_payment(Decimal("0.0051"))) == "0.01"
    assert str(_round_payment(Decimal("1000000.3433"))) == "1000000.34"
    assert str(_round_payment(Decimal("1000000.3459"))) == "1000000.35"


def test_get_month_pay():
    assert _get_month_pay("28.09.2013", "28.05.2033", "731957.77", "12.25") == Decimal("8220.05")
    assert _get_month_pay("21.12.2011", "21.12.2016", "500000", "16.65") == Decimal("12332.39")
    assert _get_month_pay("26.12.2011", "26.12.2016", "500000", "16.65") == Decimal("12332.39")
    assert _get_month_pay("17.05.2012", "17.05.2017", "450000", "17.5") == Decimal("11305")
