from . import add
from ebb import ui
from ebb.models import *

@add('add-account')
def run(session):
    account_name = ui.prompt('Account name:')
    currency = ui.prompt_model('Currency:', session, Currency, lambda currency: currency.code)

    account = Account(name=account_name, currency=currency)
    session.add(account)

    if ui.confirm('Confirm', default=False):
        try:
            session.commit()
            ui.print('Account added')
        except:
            ui.print('Adding account failed')
    else:
        session.rollback()
        ui.print('Account not added')
