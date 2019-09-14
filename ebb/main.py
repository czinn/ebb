from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prompt_toolkit.history import InMemoryHistory

from db import Session
from ui import prompt_options
from commands import command_list, get_command

def main():
    history = InMemoryHistory()
    while(True):
        command_name = prompt_options('>', command_list(), strict=True, history=history)
        try:
            command = get_command(command_name)
        except:
            print('Invalid command')
            continue
        command(Session())

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        pass
