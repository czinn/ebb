import importlib
import os
import glob

registry = {}

def add(name):
    def inner(f):
        registry[name] = f
        return f
    return inner

def command_list():
    return list(registry.keys())

def get(command):
    return registry[command]

module_paths = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
for module_path in module_paths:
    if '__init__' in module_path: continue
    module_name = module_path[:-3].split('/')[-1]
    command_name = module_name.replace('_', '-')
    module = importlib.import_module(f'commands.{module_name}')
