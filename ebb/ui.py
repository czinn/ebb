import re

from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt as p
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.validation import Validator, ValidationError

class RegexValidator(Validator):
    def __init__(self, pattern, error_message, has_default=False):
        self.regex = re.compile(pattern)
        self.error_message = error_message
        self.has_default = has_default

    def validate(self, document):
        text = document.text
        if self.has_default and len(text) == 0:
            return
        match = self.regex.match(text)
        fail_i = None
        if match is None:
            fail_i = 0
        elif match.end() < len(text):
            fail_i = match.end()
        if fail_i is not None:
            raise ValidationError(message=self.error_message,  cursor_position=fail_i)

def prompt(message, default=None):
    result = p(message +  ' ', vi_mode=True)
    if default is not None and result == '':
        return default
    return result

def prompt_integer(message, default=None):
    validator = RegexValidator('0|[1-9][0-9]*', 'Enter an integer',
            default is not None)
    result = p(message + ' ', vi_mode=True, validator=validator)
    if default is not None and result == '':
        return default
    return int(result)

def prompt_number(message, default=None):
    validator = RegexValidator('([1-9][0-9]*\\.?|0?\\.)[0-9]*|0',
            'Enter a number', default is not None)
    result = p(message + ' ', vi_mode=True, validator=validator)
    if default is not None and result == '':
        return default
    return float(result)

def confirm(message, default=None):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        yn = " [yn] "
    elif default:
        yn = " [Yn] "
    elif not default:
        yn = " [yN] "

    while True:
        choice = prompt(message + yn).lower()
        if default is not None and choice == '':
            return default
        elif choice in valid:
            return valid[choice]
        else:
            print('Please respond with \'yes\' or \'no\' (or \'y\' or \'n\').')

def prompt_options(message, options, strict=False, history=None):
    completer = FuzzyWordCompleter(options, WORD=True)
    if strict:
        validator = Validator.from_callable(lambda s: s in options,
                error_message='', move_cursor_to_end=False)
        return p(message + ' ', completer=completer, vi_mode=True,
                validator=validator, history=history)
    return p(message + ' ', completer=completer, vi_mode=True, history=history)

def prompt_model(message, session, model_cls, to_string, of_string=None):
    models = session.query(model_cls).all()
    model_map = {to_string(m): m for m in models}
    selection = prompt_options(message, model_map.keys(), strict=of_string is None)
    if selection not in model_map:
        selected_model = of_string(selection)
        session.add(selected_model)
    else:
        selected_model = model_map[selection]
    return selected_model
