from prompt_toolkit.formatted_text import HTML

from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import get_account_balance

@add('show-accounts')
def run(session):
    accounts = session.query(Account).all()
    columns = [Column('Account', 'l', 30), Column('Currency', 'l', 8),
            Column('Balance', 'r', 20)]
    balances = [get_account_balance(session, a) for a in accounts]
    usd = session.query(Currency).filter(Currency.code == 'USD').one()
    total_balance = Money(sum(balance.usd_amount() for balance in balances), usd)
    data = [[a.name, a.currency.code, balance] for a, balance in zip(accounts, balances)]
    data.append([HTML('<b>Total</b>'), usd.code, total_balance])
    draw_table(columns, data)
