from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Session
from commands import command_list, get

session = Session()

def main():
    print(command_list())

if __name__ == '__main__':
    main()
