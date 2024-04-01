from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

database_url = 'sqlite:///test_DB.db'
engine = create_engine(database_url, echo=True)

Session = sessionmaker(bind=engine)