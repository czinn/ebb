from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import get_account_balance

@add('show-accounts')
def run(session):
    accounts = session.query(Account).all()
    columns = [Column('Account', 'l', 30), Column('Currency', 'l', 8),
            Column('Balance', 'r', 20)]
    data = [[a.name, a.currency.code, str(get_account_balance(session, a))] for a in accounts]
    draw_table(columns, data)
