import datetime

from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import get_account_balance

@add('add-transfer', commit=True)
def run(session):
    from_account = prompt_model('From account:', session, Account, lambda account: account.name)
    to_account = prompt_model('From account:', session, Account, lambda account: account.name)
    from_date = prompt_date('From date (today):', default=datetime.date.today())
    to_date = prompt_date(f'To date ({from_date.isoformat()}):', default=from_date)
    from_money = prompt_money('Amount:', from_account.currency)
    if from_account.currency != to_account.currency:
        to_money = prompt_money(f'To amount (in {to_account.currency.code}):',
                to_account.currency)
    else:
        # TODO: add support for fees in the case of same-currency transfers (or
        # don't and let that just be a complex transaction)
        to_money = from_money

    transaction = Transaction()
    from_delta = BalanceDelta(account=from_account, transaction=transaction,
            date=from_date, amount=-abs(from_money.amount))
    to_delta = BalanceDelta(account=to_account, transaction=transaction,
            date=from_date, amount=abs(to_money.amount))
    session.add(transaction)
    session.add(from_delta)
    session.add(to_delta)
