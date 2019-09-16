import datetime

from prompt_toolkit.formatted_text import HTML

from . import add
from ebb.models import *
from ebb.ui import *
from ebb.queries import get_account_balance
from ebb.money_bag import MoneyBag

@add('add-complex-transaction', commit=True)
def run(session):
    transaction = Transaction()
    deltas = []
    flows = []
    money_bag = MoneyBag()
    last_date = datetime.date.today()

    while True:
        print(HTML(f'<b>Delta {len(deltas) + 1}</b>'))
        account = prompt_model('Account:', session, Account, lambda account: account.name)
        date = prompt_date(f'Date ({last_date.isoformat()}):', default=last_date)
        last_date = date
        money = prompt_money(f'Amount ({account.currency.code}):', account.currency)
        money_bag.add_money(money)

        delta = BalanceDelta(transaction=transaction, account=account,
                date=date, amount=money.amount)
        deltas.append(delta)

        if not confirm('Add another delta?'):
            break

    while True:
        print(HTML(f'<b>Flow {len(flows) + 1}</b>'))
        date = prompt_date(f'Date ({last_date.isoformat()}):', default=last_date)
        last_date = date
        payee = prompt_model('Payee:', session, Payee, lambda payee: payee.name,
                lambda name: Payee(name=name))

        # Find the most recent category for that payee, for a default
        # TODO: dedup this block with the one in simple_transaction
        recent_category_flow = session.query(Flow).filter(Flow.payee == payee) \
                .order_by(Flow.date.desc()).first()
        if recent_category_flow is not None:
            recent_category = recent_category_flow.category
            category = prompt_model(f'Category ({recent_category.name}):', session,
                    Category, lambda category: category.name, nullable=True)
            if category is None:
                category = recent_category
        else:
            category = prompt_model('Category:', session, Category,
                    lambda category: category.name)

        current_currencies = money_bag.currencies()
        if len(current_currencies) == 1:
            currency = prompt_model(f'Currency ({current_currencies[0].code}):',
                    session, Currency, lambda currency: currency.code, nullable=True)
            if currency is None:
                currency = current_currencies[0]
        else:
            currency = prompt_model(f'Currency ({current_currencies[0].code}):',
                    session, Currency, lambda currency: currency.code)
        default_amount = money_bag.money_in_currency(currency)
        money = prompt_money(f'Amount ({default_amount}):', currency,
                default=default_amount.major_amount)
        money_bag.subtract_money(money)

        # TODO: dedup description, dat, and dal with same blocks in simple_transaction
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

        flow = Flow(transaction=transaction, category=category, payee=payee,
                date=date, description=description, amount=money.amount,
                currency=currency, amortization_type=amortization_type,
                amortization_length=amortization_length)
        flows.append(transaction)

        if not confirm('Add another flow?'):
            break

    session.add(transaction)
    session.add_all(deltas)
    session.add_all(flows)
