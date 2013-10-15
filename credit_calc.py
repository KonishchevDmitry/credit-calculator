from datetime import datetime as Date

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


def _parse_date(string):
    try:
        return Date.strptime(string, DATE_FORMAT)
    except ValueError:
        raise InvalidDateError(string)
