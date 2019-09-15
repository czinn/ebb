from collections import defaultdict

from ebb.models import Money

class MoneyBag():
    def __init__(self):
        self.currency_map = {}
        self.amount_map = defaultdict(int)

    def moneys(self):
        return [Money(amount, self.currency_map[code]) for code, amount in
                self.amount_map.items() if amount != 0]

    def currencies(self):
        return [self.currency_map[code] for code, amount in
                self.amount_map.items() if amount != 0]

    def add_money(self, money):
        code = money.currency.code
        self.currency_map[code] = money.currency
        self.amount_map[code] += money.amount

    def subtract_money(self, money):
        code = money.currency.code
        self.currency_map[code] = money.currency
        self.amount_map[code] -= money.amount

    def money_in_currency(self, currency):
        return Money(self.amount_map[currency.code], currency)
