from prompt_toolkit.formatted_text import HTML

from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import get_account_transactions

def data_for_balance_delta(account, transaction, balance_delta):
    return [str(transaction.id) if balance_delta.account.id == account.id else None,
        str(balance_delta.date), Money(balance_delta.amount,
        balance_delta.account.currency), None if balance_delta.account.id ==
        account.id else balance_delta.account.name, None]

def data_for_flow(flow):
    return [None, None, Money(flow.amount, flow.currency), flow.payee.name, flow.description]

class MergeError(Exception):
    pass

def merge_values(value1, value2):
    if value1 is None: return value2
    if value2 is None: return value1
    if value1 == value2: return value1
    raise MergeError()

def data_for_transaction(account, transaction):
    # Render a line for each component of the transaction, and put the balance
    # delta for this account first
    data = [data_for_balance_delta(account, transaction, balance_delta)
                    for balance_delta in transaction.balance_deltas] + \
            [data_for_flow(flow) for flow in transaction.flows]
    data.sort(key=lambda x:x[0] is None)
    # If there are only two lines, see if they can be merged
    if len(data) == 2:
        try:
            data = [[merge_values(value1, value2) for value1, value2 in
                zip(data[0], data[1])]]
        except MergeError:
            pass
    return [[x if x is not None else "" for x in data] for data in data]

@add('show-transactions')
def run(session):
    account = prompt_model('Account:', session, Account, lambda account: account.name)
    transactions = get_account_transactions(session, account, limit=100)

    columns = [Column('ID', 'l', 4), Column('Date', 'l', 10),
            Column('Amount', 'l', 30), Column('Payee', 'l', 40),
            Column('Description', 'l', 80)]
    data = []
    for transaction in transactions:
        data += data_for_transaction(account, transaction)
    draw_table(columns, data)
