import datetime

from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import get_account_balance

@add('add-simple-transaction', commit=True)
def run(session):
    account = prompt_model('Account:', session, Account, lambda account: account.name)
    date = prompt_date('Date (today):', default=datetime.date.today())
    payee = prompt_model('Payee:', session, Payee, lambda payee: payee.name,
            lambda name: Payee(name=name))

    # Find the most recent category for that payee, for a default
    recent_category = session.query(Flow).filter(Flow.payee == payee) \
            .order_by(Flow.date.desc()).first().category
    if recent_category is not None:
        category = prompt_model(f'Category ({recent_category.name}):', session,
                Category, lambda category: category.name, nullable=True)
        if category is None:
            category = recent_category
    else:
        category = prompt_model('Category:', session, Category, lambda category: category.name)

    money = prompt_money(f'Amount ({account.currency.code}):', account.currency)
    description = prompt('Description:', nullable=True)
    if description == '':
        description = None

    dat = category.default_amortization_type or AmortizationType.LINEAR
    amortization_type = prompt_enum(f'Amortization type ({dat.name.title()}):',
            AmortizationType, default=dat)
    if amortization_type == category.default_amortization_type:
        amortization_type = None # use category default

    dal = category.default_amortization_length or 1
    amortization_length = prompt_integer(f'Amortization length (days) ({dal}):',
            default=dal)
    if amortization_length == category.default_amortization_length:
        amortization_length = None # use category default

    transaction = Transaction()
    balance_delta = BalanceDelta(account=account, transaction=transaction,
            date=date, amount=money.amount)
    flow = Flow(transaction=transaction, category=category, payee=payee,
            date=date, description=description, amount=money.amount,
            currency=account.currency, amortization_type=amortization_type,
            amortization_length=amortization_length)
    session.add(transaction)
    session.add(balance_delta)
    session.add(flow)
