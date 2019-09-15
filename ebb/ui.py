import re
from collections import namedtuple

from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt as p
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.formatted_text import to_formatted_text, fragment_list_width, HTML, FormattedText

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

class NonemptyValidator(Validator):
    def validate(self, document):
        text = document.text
        if len(text) == 0:
            raise ValidationError(message='Input must not be empty', cursor_position=0)

def prompt(message, regex=None, regex_error='Invalid input', default=None, history=None, completer=None):
    validator = RegexValidator(regex, regex_error, default is not None) \
            if regex else NonemptyValidator()
    result = p(message +  ' ', vi_mode=True, history=history,
            validator=validator, completer=completer)
    if default is not None and result == '':
        return default
    return result

def prompt_integer(message, default=None, history=None):
    default = str(default) if default is not None else None
    return int(prompt(message, default=default, regex='0|-?[1-9][0-9]*',
        regex_error='Enter an integer', history=history))

def prompt_number(message, default=None, history=None):
    default = str(default) if default is not None else None
    return float(prompt(message, default=default,
        regex='-?([1-9][0-9]*\\.?|0?\\.)[0-9]*|0', regex_error='Enter a number',
        history=history))

def confirm(message, default=None):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    default_value = None
    if default is None:
        yn = " [yn]:"
    elif default:
        yn = " [Yn]:"
        default_value = 'y'
    elif not default:
        yn = " [yN]:"
        default_value = 'n'

    while True:
        choice = prompt(message + yn, regex='y(es?)?|no?', default=default_value).lower()
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
    return prompt(message, completer=completer, history=history)

def prompt_model(message, session, model_cls, to_string, of_string=None, nullable=False):
    models = session.query(model_cls).all()
    model_map = {to_string(m): m for m in models}
    options = list(model_map.keys())
    if nullable:
        options.append('')
    selection = prompt_options(message, options, strict=of_string is None)
    if selection not in model_map:
        if selection == '':
            return None
        selected_model = of_string(selection)
        session.add(selected_model)
    else:
        selected_model = model_map[selection]
    return selected_model

def prompt_enum(message, enum, default=None, **kwargs):
    options = [key.title() for key in enum.__members__.keys()]
    if default is not None:
        options.append('')
    selection = prompt_options(message, options, strict=True, **kwargs).upper()
    if selection not in enum.__members__:
        return default
    return enum.__members__[selection]

def trim_pad(formatted_text, width, align):
    text_width = fragment_list_width(formatted_text)
    if text_width == width:
        return formatted_text
    if text_width < width:
        left_pad = width - text_width if align == 'r' else 0
        right_pad = width - text_width if align == 'l' else 0
        return [('', ' ' * left_pad)] + formatted_text + [('', ' ' * right_pad)]
    trimmed = []
    width -= 3
    while fragment_list_width(trimmed) < width:
        trimmed.append(formatted_text.pop(0))
    if fragment_list_width(trimmed) > width:
        trimmed[-1] = (trimmed[-1][0],
                trimmed[-1][1][:-(fragment_list_width(trimmed) - width)])
    return trimmed + [('', '...')]

Column = namedtuple('Column', ['header', 'align', 'max_width'])
def draw_table(columns, data):
    column_widths = [0 for _ in columns]
    data = [[to_formatted_text(cell) for cell in row] for row in data]
    for row in data:
        for i, cell in enumerate(row):
            column_widths[i] = max(column_widths[i], fragment_list_width(cell))
    row_output = []
    for i, column in enumerate(columns):
        column_widths[i] = max(column_widths[i], len(column.header))
        column_widths[i] = min(column_widths[i], column.max_width)
        row_output += trim_pad(to_formatted_text(HTML(f'<b>{column.header}</b>')),
                column_widths[i], 'l') + [('', '  ')]
    print(FormattedText(row_output))
    for row in data:
        row_output = []
        for i, cell in enumerate(row):
            row_output += trim_pad(cell, column_widths[i], columns[i].align) + \
                    [('', '  ')]
        print(FormattedText(row_output))
