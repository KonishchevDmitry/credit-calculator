from decimal import Decimal, DecimalException

from object_validator import validate
from object_validator import InvalidValueError
from object_validator import String, List, Dict, DictScheme

import python_config

from credit_calc.util import InvalidDateError
from credit_calc.util import get_date


class _Date(String):
    def validate(self, obj):
        super(_Date, self).validate(obj)

        try:
            return get_date(obj)
        except InvalidDateError:
            raise InvalidValueError(obj)


class _Amount(String):
    def validate(self, obj):
        super(_Amount, self).validate(obj)

        try:
            amount = Decimal(obj)
        except DecimalException:
            raise InvalidValueError(obj)

        if amount <= 0:
            raise InvalidValueError(obj)

        return amount


class _Interest(String):
    def validate(self, obj):
        super(_Interest, self).validate(obj)

        try:
            interest = Decimal(obj)
        except DecimalException:
            raise InvalidValueError(obj)

        if interest <= 0 or interest >= 100:
            raise InvalidValueError(obj)

        return interest


def get_credits(config_path):
    return _get_config(config_path)["credits"]


def _get_config(config_path):
    config = python_config.load(config_path)

    try:
        return validate("config", config, DictScheme({
            "credits": List(DictScheme({
                "amount":     _Amount(),
                "interest":   _Interest(),
                "start_date": _Date(),
                "end_date":   _Date(),
                "payments":   Dict(_Date(), _Amount(), optional=True),
            }))
        }))
    except Exception as e:
        raise Exception("Error while parsing '{}' configuration file: {}".format(config_path, e))
