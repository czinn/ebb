import datetime

from . import add
from ebb.models import *
from ebb.ui import *

@add('add-account', commit=True)
def run(session):
    account_name = prompt('Account name:')
    currency = prompt_model('Currency:', session, Currency, lambda currency: currency.code)

    current_balance = prompt_money('Current balance:', currency)

    account = Account(name=account_name, currency=currency)
    balance = Balance(account=account, date=datetime.date.today(),
            amount=current_balance.amount)
    session.add(account)
    session.add(balance)
