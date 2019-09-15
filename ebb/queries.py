import datetime

from sqlalchemy.sql import func

from ebb.models import *

# Computes the account's current balance by finding the most recent Balance and
# summing all balance updates since then
def get_account_balance(session, account, as_of=datetime.date.today()):
    latest_balance = session.query(Balance).filter(Balance.account==account,
            Balance.date <= as_of).order_by(Balance.date.desc()).first()
    balance_amount = 0
    balance_date = datetime.date.min
    if latest_balance is not None:
        balance_amount = latest_balance.amount
        balance_date = latest_balance.date

    update_sum = session.query(func.coalesce(func.sum(BalanceDelta.amount), 0)) \
            .filter(BalanceDelta.account==account,
                    BalanceDelta.date > balance_date,
                    BalanceDelta.date <= as_of).one()[0]

    return Money(balance_amount + update_sum, account.currency)

# Get all transactions that modified the balance of an account between the
# start and end dates.
def get_account_transactions(session, account, start=datetime.date.min,
        end=datetime.date.max):
    return session.query(Transaction).join(BalanceDelta) \
            .filter(BalanceDelta.account == account) \
            .filter(BalanceDelta.date >= start) \
            .filter(BalanceDelta.date <= end).all()
