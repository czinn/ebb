from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *

Session = sessionmaker()

def connect(engine_url):
    engine = create_engine(engine_url)
    Session.configure(bind=engine)
