from . import add
from ebb.models import *
from ebb.ui import *

@add('add-category', commit=True)
def run(session):
    name = prompt('Name:')
    def of_string(text):
        if text == '': return None
    parent = prompt_model('Parent (None):', session, Category,
            lambda category: category.name, nullable=True)
    dat = parent.default_amortization_type if parent is not None else AmortizationType.LINEAR
    default_amortization_type = prompt_enum(f'Default amortization type ({dat.name.title()}):',
            AmortizationType, default=dat)
    dal = parent.default_amortization_length if parent is not None else 1
    default_amortization_length = prompt_integer(
            f'Default amortization length (days) ({dal}):', default=dal)

    category = Category(name=name, parent=parent,
            default_amortization_type=default_amortization_type,
            default_amortization_length=default_amortization_length)
    session.add(category)
