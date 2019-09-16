import datetime

from . import add
from ebb.models import *
from ebb.ui import *

@add('add-account', commit=True)
def run(session):
    account_name = prompt('Account name:')
    currency = prompt_model('Currency:', session, Currency, lambda currency: currency.code)

    account = Account(name=account_name, currency=currency)
    session.add(account)
