import importlib
import os
import glob
from functools import wraps

from ebb import ui

registry = {}

def add(name, commit=False):
    def inner(f):
        @wraps(f)
        def run(session):
            f(session)
            if commit:
                if ui.confirm('Confirm', default=False):
                    try:
                        session.commit()
                        ui.print('Success')
                    except:
                        ui.print('Failure')
                else:
                    session.rollback()
                    ui.print('Command cancelled')
        registry[name] = run
        return run
    return inner

def command_list():
    return list(registry.keys())

def get_command(command):
    return registry[command]

module_paths = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
for module_path in module_paths:
    if '__init__' in module_path: continue
    module_name = module_path[:-3].split('/')[-1]
    command_name = module_name.replace('_', '-')
    module = importlib.import_module(f'commands.{module_name}')
