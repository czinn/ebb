from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *

engine = create_engine('sqlite:///db.sqlite3', echo=True)
Session = sessionmaker(bind=engine)
