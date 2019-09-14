from . import add
from ebb.models import *
from ebb.ui import *

@add('add-currency', commit=True)
def run(session):
    code = prompt('Currency code:')
    major = prompt_integer('Major currency units (100):', default=100)
    equivalent_usd = prompt_number('USD for 1 ' + code + ':')

    currency = Currency(code=code, major=major, equivalent_usd=equivalent_usd)
    session.add(currency)
