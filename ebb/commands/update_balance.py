import datetime

from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import get_account_balance

@add('update-balance', commit=True)
def run(session):
    account = prompt_model('Account:', session, Account, lambda account: account.name)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    date = prompt_date('Date (yesterday):', default=yesterday)
    current_money = get_account_balance(session, account, as_of=date)
    money = prompt_money(f'Balance ({current_money}):', account.currency,
            default=current_money.major_amount)

    balance = Balance(account=account, date=date, amount=money.amount)
    session.add(balance)
