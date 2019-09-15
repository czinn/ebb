import datetime

from . import add
from ebb.models import *
from ebb.ui import *

@add('update-balance', commit=True)
def run(session):
    account = prompt_model('Account:', session, Account, lambda account: account.name)
    date = prompt_date('Date (today):', default=datetime.date.today())
    money = prompt_money('Balance:', account.currency)

    balance = Balance(account=account, date=date, amount=money.amount)
    session.add(balance)
