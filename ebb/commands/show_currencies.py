from . import add
from ebb.models import *
from ebb.ui import *

@add('show-currencies')
def run(session):
    currencies = session.query(Currency).all()
    columns = [Column('Code', 'l', 5), Column('Value in USD', 'r', 15)]
    data = [[c.code, f'{c.equivalent_usd:.4f}'] for c in currencies]
    draw_table(columns, data)
