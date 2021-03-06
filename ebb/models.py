import enum
from collections import namedtuple

from prompt_toolkit.formatted_text import HTML
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class Currency(Base):
    __tablename__ = 'currencies'

    id = Column(Integer, primary_key=True, nullable=False)
    # ISO 4217 currency code
    code = Column(String, nullable=False)
    # Number of minor currency units in one major unit (e.g. 100 USd in 1 USD)
    major = Column(Integer, nullable=False)
    # Equivalent USD of one major unit (e.g. 1.0 for USD, ~0.7543 for CAD)
    equivalent_usd = Column(Float, nullable=False)

    def __repr__(self):
        return '<Currency(code={}, major={}, equivalent_usd={:.2f})>'.format(
                self.code, self.major, self.equivalent_usd)

class Money(namedtuple('Money', ['amount', 'currency'])):
    def __str__(self):
        sign = '+' if self.amount > 0 else '' if self.amount == 0 else '-'
        return f'{sign}${abs(self.major_amount):.2f}'

    def __pt_formatted_text__(self):
        colour = 'green' if self.amount > 0 else 'white' if self.amount == 0 else 'red'
        return HTML(f'<{colour}>{self}</{colour}>').__pt_formatted_text__()

    @property
    def major_amount(self):
        return self.amount / self.currency.major

    def usd_amount(self):
        return int(round(self.amount / self.currency.major * \
                self.currency.equivalent_usd * 100))

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, nullable=False)
    # Name of the account (e.g. Cash, PayPal)
    name = Column(String, nullable=False)
    # Currency associated with the account
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    currency = relationship('Currency')

    def __repr__(self):
        return '<Account(name={}, currency={})>'.format(
                self.name, self.currency.code)

class Balance(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True)
    # Account associated with the balance
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account')
    # Date as of which the balance was current
    # The balance should include all transactions in the account made on the
    # date in question
    date = Column(Date, nullable=False)
    # Amount of currency, in units of the currency associated with the account
    amount = Column(Integer, nullable=False)

    def __repr__(self):
        return '<Balance(account={}, date={}, amount={})>'.format(
                self.account.name, self.date, self.amount)

class AmortizationType(enum.Enum):
    LINEAR = 1
    DECLINING = 2

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    # Name for the category
    name = Column(String, nullable=False)
    # Parent category
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    subcategories = relationship('Category', backref=backref('parent', remote_side=[id]))
    # Default amortization type (see Flow for details)
    default_amortization_type = Column(Enum(AmortizationType), nullable=True)
    # Default amortization duration (see Flow for details)
    default_amortization_length = Column(Integer, nullable=True)

    def __repr__(self):
        if self.parent_id is not None:
            return '<Category(name={}, parent={})>'.format(
                    self.name, self.parent.name)
        else:
            return '<Category(name={})'.format(self.name)

class Payee(Base):
    __tablename__ = 'payees'

    id = Column(Integer, primary_key=True)
    # Payee name
    name = Column(String, nullable=False)

    def __str__(self):
        return '<Payee(name={})'.format(self.name)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, nullable=False)
    # Associated balance deltas
    balance_deltas = relationship('BalanceDelta', back_populates='transaction')
    # Associated flows
    flows = relationship('Flow', back_populates='transaction')
    
    def __repr__(self):
        return '<Transaction(id={})'.format(id)

class BalanceDelta(Base):
    __tablename__ = 'balance_deltas'

    id = Column(Integer, primary_key=True)
    # Transaction associated with the delta
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    transaction = relationship('Transaction', back_populates='balance_deltas')
    # Account associated with the delta
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account')
    # Date on which delta occurred (for real, not the posting date)
    date = Column(Date, nullable=False)
    # Amount (negative for debit, positive for credit)
    amount = Column(Integer, nullable=False)

    def __repr__(self):
        return '<BalanceDelta(transaction={}, account={}, date={}, amount={})>'.format(
                self.transaction_id, self.account.name, self.date, self.amount)

    @property
    def money(self):
        return Money(self.amount, self.account.currency)

class Flow(Base):
    __tablename__ = 'flows'

    id = Column(Integer, primary_key=True)
    # Transaction associated with the flow
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    transaction = relationship('Transaction', back_populates='flows')
    # Category for the flow
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship('Category')
    # Payee (or payer, for income) for the flow
    payee_id = Column(Integer, ForeignKey('payees.id'), nullable=False)
    payee = relationship('Payee')
    # Date on which delta occurred (for real, not the posting date)
    date = Column(Date, nullable=False)
    # Description of the flow
    description = Column(String, nullable=True)
    # Amount (negative for debit, positive for credit)
    amount = Column(Integer, nullable=False)
    # Currency associated with the flow
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    currency = relationship('Currency')
    # How the flow should be amortized
    amortization_type = Column(Enum(AmortizationType), nullable=True)
    # Duration over which flow should be amortized (note that for e.g.
    # declining balance amortizations, the flow will actually show debits past
    # the "end date" of the amortization; this field is for scaling).
    amortization_length = Column(Integer, nullable=True)

    def __repr__(self):
        return '<Flow(date={}, transaction={}, category={}, payee={},\
                description={}, amount={}, amortization=({}, {}))>'.format(
                        self.date, self.transaction_id, self.category.name,
                        self.payee.name, self.description, self.amount,
                        self.amortization_type, self.amortization_length)

    @property
    def money(self):
        return Money(self.amount, self.currency)

    def amount_on_date(self, date):
        if date < self.date:
            return Money(0, self.currency)
        amortization_type = self.amortization_type or \
                self.category.default_amortization_type
        amortization_length = self.amortization_length or \
                self.category.default_amortization_length
        days_since_start = (date - self.date).days
        if amortization_type == AmortizationType.LINEAR:
            if days_since_start >= amortization_length:
                return Money(0, self.currency)
            return Money(int(round(self.amount / amortization_length)), self.currency)
        elif amortization_type == AmortizationType.DECLINING:
            decline_rate = 2 / amortization_length
            return Money(int(round(self.amount * (1 - decline_rate) ** \
                    days_since_start * decline_rate)), self.currency)

    # TODO: write and use formulae that compute the amount for a date range in one step
