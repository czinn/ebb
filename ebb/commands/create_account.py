from . import add
from ebb import ui
from ebb.models import *

@add('add-account', commit=True)
def run(session):
    account_name = ui.prompt('Account name:')
    currency = ui.prompt_model('Currency:', session, Currency, lambda currency: currency.code)

    account = Account(name=account_name, currency=currency)
    session.add(account)
