from . import add
from ebb.models import *
from ebb.ui import *

@add('show-accounts')
def run(session):
    accounts = session.query(Account).all()
    columns = [Column('Account', 'l', 30), Column('Currency', 'l', 8)]
    data = [[a.name, a.currency.code] for a in accounts]
    draw_table(columns, data)
