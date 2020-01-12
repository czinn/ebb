import datetime
from collections import defaultdict

from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload

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
def get_account_transactions(session, account, start=None,
        end=None, limit=None):
    query = session.query(Transaction).join(BalanceDelta) \
            .filter(BalanceDelta.account == account) \
            .options(joinedload(Transaction.balance_deltas)) \
            .options(joinedload(Transaction.flows)) \
            .order_by(BalanceDelta.date.desc())

    if start is not None:
        query = query.filter(BalanceDelta.date >= start)
    if end is not None:
        query = query.filter(BalanceDelta.date <= end)
    if limit is not None:
        query = query.limit(limit)
    return query.all()

def spending_by_category(session, start=datetime.date.min, end=datetime.date.max):
    # TODO: filter this to only include relevant transactions
    flows = session.query(Flow).options(joinedload(Flow.category)).all()
    spending = defaultdict(float)
    day = datetime.timedelta(days=1)
    for flow in flows:
        date = start
        while date <= end:
            spending[flow.category.name] += flow.amount_on_date(date).usd_amount()
            date += day
    return { key: int(round(value)) for key, value in spending.items() }
