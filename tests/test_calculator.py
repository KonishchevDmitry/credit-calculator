import pytest

from decimal import Decimal
from datetime import date as Date

from credit_calc.util import InvalidDateError
from credit_calc.util import get_date

from credit_calc.calculator import Credit, MonthInterest
from credit_calc.calculator import InvalidDateRangeError
from credit_calc.calculator import InvalidPaymentError, InvalidPaymentDateError

from credit_calc.calculator import get_credit_info
from credit_calc.calculator import _nearest_valid_date
from credit_calc.calculator import _iter_months, _iter_month_interest, _count_months
from credit_calc.calculator import _round_payment, _get_month_pay, _calculate


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
        get_date("15.03.2013"), get_date("15.04.2013"), get_date("15.05.2013") ]

def test_iter_months_from_year_to_year():
    assert list(_iter_months("15.11.2013", "15.02.2014")) == [
        get_date("15.11.2013"), get_date("15.12.2013"),
        get_date("15.01.2014"), get_date("15.02.2014") ]

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
        get_date("31.12.2012"), get_date("31.01.2013"),
        get_date("28.02.2013"), get_date("31.03.2013"),
        get_date("30.04.2013") ]


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


def test_calculate_with_invalid_payment_date():
    with pytest.raises(InvalidPaymentDateError):
        _calculate("17.05.2012", "17.05.2017", "450000", "17.5", {
            "19.06.2013": "100000"
        })

def test_calculate_with_invalid_payment():
    with pytest.raises(InvalidPaymentError):
        _calculate("17.05.2012", "17.05.2017", "450000", "17.5", {
            "17.06.2012": "1"
        })

def test_calculate_450():
    schedule = _calculate("17.05.2012", "17.05.2017", "450000", "17.5")
    _check_payment(schedule[0], "17.06.2012", "4634.92", "6670.08", "11305.00")
    _check_payment(schedule[1], "17.07.2012", "4916.57", "6388.43", "11305.00")
    _check_payment(schedule[-2], "17.04.2017", "10973.68", "331.32", "11305.00")
    _check_payment(schedule[-1], "17.05.2017", "11317.87", "162.79", "11480.66")


    schedule = _calculate("17.05.2012", "17.05.2017", "450000", "17.5", {
        "17.06.2012": "14125.22",
    })
    _check_payment(schedule[0], "17.06.2012", "7455.14", "6670.08", "14125.22")
    _check_payment(schedule[1], "17.07.2012", "4888.14", "6347.98", "11236.12")
    _check_payment(schedule[-2], "17.04.2017", "10910.44", "325.68", "11236.12")
    _check_payment(schedule[-1], "17.05.2017", "11001.95", "158.25", "11160.20")


    schedule = _calculate("17.05.2012", "17.05.2017", "450000", "17.5", {
        "17.06.2012": "14125.22",
        "17.08.2012": "19020.00",
    })

    right_schedule = (
        ("17.06.2012",  "7455.14", "6670.08", "14125.22"),
        ("17.07.2012",  "4888.14", "6347.98", "11236.12"),
        ("17.08.2012", "12532.88", "6487.12", "19020.00"),
        ("17.09.2012",  "4732.66", "6301.36", "11034.02"),
        ("17.10.2012",  "5003.82", "6030.20", "11034.02"),
        ("17.11.2012",  "4876.98", "6157.04", "11034.02"),
        ("17.12.2012",  "5145.55", "5888.47", "11034.02"),
        ("17.01.2013",  "5016.51", "6017.51", "11034.02"),
        ("17.02.2013",  "5083.64", "5950.38", "11034.02"),
        ("17.03.2013",  "5727.73", "5306.29", "11034.02"),
        ("17.04.2013",  "5244.33", "5789.69", "11034.02"),
        ("17.05.2013",  "5506.52", "5527.50", "11034.02"),
        ("17.06.2013",  "5404.12", "5629.90", "11034.02"),
        ("17.07.2013",  "5663.46", "5370.56", "11034.02"),
        ("17.08.2013",  "5568.61", "5465.41", "11034.02"),
        ("17.09.2013",  "5651.38", "5382.64", "11034.02"),
        ("17.10.2013",  "5906.30", "5127.72", "11034.02"),
        ("17.11.2013",  "5823.16", "5210.86", "11034.02"),
        ("17.12.2013",  "6075.01", "4959.01", "11034.02"),
        ("17.01.2014",  "6000.01", "5034.01", "11034.02"),
        ("17.02.2014",  "6089.18", "4944.84", "11034.02"),
        ("17.03.2014",  "6649.46", "4384.56", "11034.02"),
        ("17.04.2014",  "6278.52", "4755.50", "11034.02"),
        ("17.05.2014",  "6522.23", "4511.79", "11034.02"),
        ("17.06.2014",  "6468.78", "4565.24", "11034.02"),
        ("17.07.2014",  "6709.09", "4324.93", "11034.02"),
        ("17.08.2014",  "6664.64", "4369.38", "11034.02"),
        ("17.09.2014",  "6763.70", "4270.32", "11034.02"),
        ("17.10.2014",  "6998.73", "4035.29", "11034.02"),
        ("17.11.2014",  "6968.25", "4065.77", "11034.02"),
        ("17.12.2014",  "7199.63", "3834.39", "11034.02"),
        ("17.01.2015",  "7178.82", "3855.20", "11034.02"),
        ("17.02.2015",  "7285.52", "3748.50", "11034.02"),
        ("17.03.2015",  "7746.09", "3287.93", "11034.02"),
        ("17.04.2015",  "7508.94", "3525.08", "11034.02"),
        ("17.05.2015",  "7730.66", "3303.36", "11034.02"),
        ("17.06.2015",  "7735.44", "3298.58", "11034.02"),
        ("17.07.2015",  "7953.11", "3080.91", "11034.02"),
        ("17.08.2015",  "7968.62", "3065.40", "11034.02"),
        ("17.09.2015",  "8087.06", "2946.96", "11034.02"),
        ("17.10.2015",  "8298.45", "2735.57", "11034.02"),
        ("17.11.2015",  "8330.60", "2703.42", "11034.02"),
        ("17.12.2015",  "8537.63", "2496.39", "11034.02"),
        ("17.01.2016",  "8584.99", "2449.03", "11034.02"),
        ("17.02.2016",  "8715.26", "2318.76", "11034.02"),
        ("17.03.2016",  "8985.71", "2048.31", "11034.02"),
        ("17.04.2016",  "8977.63", "2056.39", "11034.02"),
        ("17.05.2016",  "9172.75", "1861.27", "11034.02"),
        ("17.06.2016",  "9246.67", "1787.35", "11034.02"),
        ("17.07.2016",  "9436.96", "1597.06", "11034.02"),
        ("17.08.2016",  "9523.60", "1510.42", "11034.02"),
        ("17.09.2016",  "9664.77", "1369.25", "11034.02"),
        ("17.10.2016",  "9847.57", "1186.45", "11034.02"),
        ("17.11.2016",  "9953.99", "1080.03", "11034.02"),
        ("17.12.2016", "10131.61",  "902.41", "11034.02"),
        ("17.01.2017", "10250.53",  "783.49", "11034.02"),
        ("17.02.2017", "10401.91",  "632.11", "11034.02"),
        ("17.03.2017", "10602.73",  "431.29", "11034.02"),
        ("17.04.2017", "10714.11",  "319.91", "11034.02"),
        ("17.05.2017", "10810.11",  "155.49", "10965.60"),
    )

    assert len(schedule) == len(right_schedule)
    for payment, right_payment in zip(schedule, right_schedule):
        _check_payment(payment, *right_payment)

def test_calculate_500_1():
    schedule = _calculate("21.12.2011", "21.12.2016", "500000", "16.65")
    _check_payment(schedule[0], "21.01.2012", "5274.93", "7057.46", "12332.39")
    _check_payment(schedule[1], "21.02.2012", "5355.55", "6976.84", "12332.39")
    _check_payment(schedule[-2], "21.11.2016", "11992.28", "340.11", "12332.39")
    _check_payment(schedule[-1], "21.12.2016", "12125.04", "165.48", "12290.52")

    schedule = _calculate("21.12.2011", "21.12.2016", "500000", "16.65", {
        "21.07.2012": "22071.39",
    })
    _check_payment(schedule[0], "21.01.2012", "5274.93", "7057.46", "12332.39")
    _check_payment(schedule[1], "21.02.2012", "5355.55", "6976.84", "12332.39")
    _check_payment(schedule[5], "21.06.2012", "5673.63", "6658.76", "12332.39")
    _check_payment(schedule[6], "21.07.2012", "15704.86", "6366.53", "22071.39")
    _check_payment(schedule[7], "21.08.2012", "5711.79", "6357.27", "12069.06")
    _check_payment(schedule[-2], "21.11.2016", "11733.51", "335.55", "12069.06")
    _check_payment(schedule[-1], "21.12.2016", "12059.88", "164.59", "12224.47")

def test_calculate_500_2():
    schedule = _calculate("26.12.2011", "26.12.2016", "500000", "16.65")
    _check_payment(schedule[0], "26.01.2012", "5278.05", "7054.34", "12332.39")
    _check_payment(schedule[1], "26.02.2012", "5355.59", "6976.80", "12332.39")
    _check_payment(schedule[-2], "26.11.2016", "11992.32", "340.07", "12332.39")
    _check_payment(schedule[-1], "26.12.2016", "12122.21", "165.44", "12287.65", overall_precision="0.05")

    schedule = _calculate("26.12.2011", "26.12.2016", "500000", "16.65", {
        "26.02.2012": "19002.39",
    })
    _check_payment(schedule[0], "26.01.2012", "5278.05", "7054.34", "12332.39")
    _check_payment(schedule[1], "26.02.2012", "12025.59", "6976.80", "19002.39")
    _check_payment(schedule[2], "26.03.2012", "5802.01", "6368.03", "12170.04")
    _check_payment(schedule[-2], "26.11.2016", "11841.39", "328.65", "12170.04")
    _check_payment(schedule[-1], "26.12.2016", "11463.24", "156.45", "11619.69")

def test_calculate_2000():
    schedule = _calculate("28.05.2013", "28.05.2033", "2000000", "12.25", {
        "28.06.2013": "110000",
        "28.07.2013": "21394.54",
        "28.08.2013": "21394.54",
        "28.09.2013": "1195000",
    })
    _check_payment(schedule[3], "28.09.2013", "1175158.16", "19841.84", "1195000.00")
    _check_payment(schedule[4], "28.10.2013", "850.34", "7369.71", "8220.05")
    _check_payment(schedule[5], "28.11.2013", "613.53", "7606.52", "8220.05")
    _check_payment(schedule[6], "28.12.2013", "865.08", "7354.97", "8220.05")
    _check_payment(schedule[7], "28.01.2014", "628.91", "7591.14", "8220.05")
    _check_payment(schedule[-6], "28.12.2032", "7751.75", "468.30", "8220.05")
    _check_payment(schedule[-5], "28.01.2033", "7815.57", "404.48", "8220.05")
    _check_payment(schedule[-4], "28.02.2033", "7896.78", "323.27", "8220.05")
    _check_payment(schedule[-3], "28.03.2033", "8002.27", "217.78", "8220.05")
    _check_payment(schedule[-2], "28.04.2033", "8062.20", "157.85", "8220.05")
    _check_payment(schedule[-1], "28.05.2033", "7109.96", "71.59", "7181.55", overall_precision="0.26")

def _check_payment(payment, date, credit_pay, interest_pay, month_pay, overall_precision="0.01"):
    def check(payment, right_payment, precision):
        right_payment = Decimal(right_payment)
        assert right_payment - precision <= payment <= right_payment + precision

    exact_precision = Decimal("0.01")
    overall_precision = Decimal(overall_precision)

    assert payment.date == get_date(date)
    check(payment.credit_pay, credit_pay, overall_precision)
    check(payment.interest_pay, interest_pay, exact_precision)
    check(payment.credit_pay + payment.interest_pay, month_pay, overall_precision)
    check(payment.month_pay, month_pay, overall_precision)


def test_get_credit_info():
    credit_config = {
        "amount":     "2000000",
        "interest":   "12.25",
        "start_date": "28.05.2013",
        "end_date":   "28.05.2033",
        "payments": {
            "28.06.2013":   "110000",
            "28.07.2013": "21394.54",
            "28.08.2013": "21394.54",
            "28.09.2013":  "1195000",
        }
    }

    def check(info_date, current_amount, month_pay):
        assert get_credit_info(info_date, **credit_config) == Credit(
            get_date(credit_config["start_date"]), get_date(credit_config["end_date"]),
            Decimal(credit_config["amount"]), Decimal(current_amount),
            Decimal(credit_config["interest"]), None if month_pay is None else Decimal(month_pay),
            _calculate(credit_config["start_date"], credit_config["end_date"],
                credit_config["amount"], credit_config["interest"], credit_config["payments"]))

    check(Date(1, 1, 1), 2000000, None)
    check("30.05.2013", 2000000, 110000)
    check("27.06.2013", 2000000, 110000)
    check("18.10.2013", "731957.77", "8220.05")
    check("1.1.2100", 0, None)
