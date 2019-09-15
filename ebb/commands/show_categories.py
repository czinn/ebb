from . import add
from ebb.models import *
from ebb.ui import *

def print_category(category, indent=0, last=False):
    if indent == 0:
        print(category.name)
    else:
        print('│  ' * (indent - 1) + ('└─ ' if last else '├─ ') + category.name)
    for i, subcategory in enumerate(category.subcategories):
        print_category(subcategory, indent + 1,
                last=(i == len(category.subcategories) - 1))

@add('show-categories')
def run(session):
    root_categories = session.query(Category).filter(Category.parent_id == None).all()
    for category in root_categories:
        print_category(category)
