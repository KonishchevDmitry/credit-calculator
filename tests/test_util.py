import pytest

from datetime import datetime as Date

from credit_calc.util import InvalidDateError
from credit_calc.util import get_date, format_date, year_days


def test_get_date():
    date = Date(2013, 3, 13)
    assert get_date(date) is date

def test_get_date_from_string():
    assert get_date("13.03.2013") == Date(2013, 3, 13)

def test_get_date_invalid():
    with pytest.raises(InvalidDateError):
        get_date("31.02.2013")


def test_format_date():
    assert format_date(Date(2013, 3, 2)) == "02.03.2013"


def test_year_days():
    assert year_days(2012) == 366
    assert year_days(2013) == 365
