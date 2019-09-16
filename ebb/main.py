import argparse

from prompt_toolkit.history import InMemoryHistory
from sqlalchemy import create_engine

from db import Session, connect
import ui
from commands import command_list, get_command

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db', help='db connection string')
    args = parser.parse_args()

    connect(args.db)

    history = InMemoryHistory()
    while(True):
        command_name = ui.prompt_options('>', command_list(), strict=True, history=history)
        try:
            command = get_command(command_name)
        except:
            ui.print('Invalid command')
            continue
        session = Session()
        try:
            command(session)
        except KeyboardInterrupt:
            session.rollback()
            ui.print('Command cancelled')

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        pass
