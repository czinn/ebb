import datetime

from prompt_toolkit.formatted_text import HTML

from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import spending_by_category

@add('spending-by-category')
def run(session):
    today = datetime.date.today()
    one_month_ago = today - datetime.timedelta(days=30)
    start = prompt_date(f'From date ({one_month_ago.isoformat()}):',
            default=one_month_ago)
    end = prompt_date(f'To date ({today.isoformat()}):', default=today)

    spending = spending_by_category(session, start=start, end=end)
    ordered_spending = list(spending.items())
    ordered_spending.sort(key=lambda x: x[1])

    usd = session.query(Currency).filter(Currency.code == 'USD').one()
    columns = [Column('Category', 'l', 40), Column('Spending', 'r', 20)]
    data = [[key, Money(value, usd)] for key, value in ordered_spending]
    draw_table(columns, data)
