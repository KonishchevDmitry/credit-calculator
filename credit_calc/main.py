import argparse
import datetime
import os
import sys

from pcli.text_table import Table, Column

from credit_calc import config
from credit_calc import calculator

from credit_calc.util import format_date


def parse_args():
    config_path = "~/.credits.conf"
    parser = argparse.ArgumentParser(description="Credit calculator")
    parser.add_argument("--config", default=os.path.expanduser(config_path),
        help="path to the credit configuration file (default is {})".format(config_path))
    parser.add_argument("--all", action="store_true", help="show all credits (not only active)")
    parser.add_argument("--schedule", action="store_true", help="show payment schedule for each credit")
    return parser.parse_args()


def print_payment_schedule(credits):
    for credit in credits:
        table = Table([
            Column("date",         "Date",        align=Column.ALIGN_CENTER ),
            Column("credit_pay",   "Credit pay",                            ),
            Column("interest_pay", "Interest pay"                           ),
            Column("total",        "Total"                                  ),
            Column("credit",       "Credit"                                 ),
        ])

        for payment in credit.schedule:
            table.add_row({
                "date":         format_date(payment.date),
                "credit_pay":   payment.credit_pay,
                "interest_pay": payment.interest_pay,
                "total":        payment.month_pay,
                "credit":       payment.credit,
            })

        table.draw("\n\nPayment schedule for {} credit from {}:".format(
            credit.amount, format_date(credit.start_date)))


def print_credits(credits, print_all, with_schedule):
    if not credits:
        print("No credits specified.")
        return

    today = datetime.date.today()

    credits = sorted((
        calculator.get_credit_info(today, **credit)
        for credit in credits
            if print_all or credit["end_date"] >= today),
        key=lambda credit: credit.end_date)

    if not credits:
        print("There are no active credits.")
        return

    table = Table([
        Column("start_date",     "Open date",      align=Column.ALIGN_CENTER                    ),
        Column("end_date",       "Close date",     align=Column.ALIGN_CENTER                    ),
        Column("amount",         "Amount"                                                       ),
        Column("interest",       "Interest"                                                     ),
        Column("current_amount", "Current amount",                                              ),
        Column("month_pay",      "Month pay",                                 hide_if_empty=True),
        Column("closed",         "Closed",         align=Column.ALIGN_CENTER, hide_if_empty=True),
    ])

    total_amount = 0
    total_month_pay = 0

    for credit in credits:
        closed = credit.end_date < today

        if not closed:
            total_amount += credit.current_amount
            if credit.month_pay is not None:
                total_month_pay += credit.month_pay

        table.add_row({
            "start_date":     format_date(credit.start_date),
            "end_date":       format_date(credit.end_date),
            "amount":         credit.amount,
            "interest":       credit.interest,
            "current_amount": credit.current_amount,
            "month_pay":      "" if credit.month_pay is None else credit.month_pay,
            "closed":         "✓" if closed else "",
        })

    if len(table.rows) > 1:
        total_row = {}

        if total_amount:
            total_row["current_amount"] = total_amount

        if total_month_pay:
            total_row["month_pay"] = total_month_pay

        if total_row:
            table.add_rows([{}, total_row])

    table.draw()

    if with_schedule:
        print_payment_schedule(credits)


def main():
    try:
        args = parse_args()
        credits = config.get_credits(args.config)
        print_credits(credits, args.all, args.schedule)
    except Exception as e:
        sys.exit("Error: {}".format(e))


if __name__ == "__main__":
    main()
