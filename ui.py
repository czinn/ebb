from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter

def prompt_options(message, options):
    return prompt(message, completer=FuzzyWordCompleter(options), vi_mode=True)
