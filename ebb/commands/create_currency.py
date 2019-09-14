from . import add
from ebb import ui
from ebb.models import *

@add('add-currency')
def run(session):
    code = ui.prompt('Currency code:')
    major = ui.prompt_integer('Major currency units (100):', default=100)
    equivalent_usd = ui.prompt_number('USD for 1 ' + code + ':')

    currency = Currency(code=code, major=major, equivalent_usd=equivalent_usd)
    session.add(currency)

    if ui.confirm('Confirm', default=False):
        try:
            session.commit()
            ui.print('Currency added')
        except:
            ui.print('Adding currency failed')
    else:
        session.rollback()
        ui.print('Currency not added')
