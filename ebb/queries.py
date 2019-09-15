import datetime

from sqlalchemy.sql import func

from ebb.models import *

# Computes the account's current balance by finding the most recent Balance and
# summing all balance updates since then
def get_account_balance(session, account):
    latest_balance = session.query(Balance).filter(Balance.account==account) \
            .order_by(Balance.date.desc()).first()
    balance_amount = 0
    balance_date = datetime.date.min
    if latest_balance is not None:
        balance_amount = latest_balance.amount
        balance_date = latest_balance.date

    update_sum = session.query(func.coalesce(func.sum(BalanceDelta.amount), 0)) \
            .filter(BalanceDelta.account==account,
                    BalanceDelta.date > balance_date).one()[0]

    return Money(balance_amount + update_sum, account.currency)
