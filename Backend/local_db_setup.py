from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy import event, DDL
from sqlalchemy.dialects.mysql import FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

database_url = 'sqlite:///test_DB.db'
engine = create_engine(database_url, echo=True)
Base = declarative_base()

# create tables for ML Algorithm Runs
class LCCDE(Base):
    __tablename__ = 'LCCDE'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(Integer, nullable=False) #is duration calculated through ML engine or here?
    run_date = Column(DateTime, default= datetime.datetime.utcnow)
    accuracy = Column(FLOAT(precision=7,scale=6))
    prec = Column(FLOAT(precision=7,scale=6))
    recall = Column(FLOAT(precision=7,scale=6))
    f1_score = Column(FLOAT(precision=7,scale=6))

class TreeBased(Base):
    __tablename__ = 'TreeBased'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(Integer, nullable=False) #is duration calculated through ML engine or here?
    run_date = Column(DateTime, default= datetime.datetime.utcnow)
    accuracy = Column(FLOAT(precision=7,scale=6))
    prec = Column(FLOAT(precision=7,scale=6))
    recall = Column(FLOAT(precision=7,scale=6))
    f1_score = Column(FLOAT(precision=7,scale=6))

class MTH(Base):
    __tablename__ = 'mth'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(Integer, nullable=False) #is duration calculated through ML engine or here?
    run_date = Column(DateTime, default= datetime.datetime.utcnow)
    accuracy = Column(FLOAT(precision=7,scale=6))
    prec = Column(FLOAT(precision=7,scale=6))
    recall = Column(FLOAT(precision=7,scale=6))
    f1_score = Column(FLOAT(precision=7,scale=6))

# Create History table for all runs
        #go back and create link between this table and others
class RunHistory(Base):
    __tablename__ = 'RunHistory'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(Integer, nullable=False)
    run_date = Column(DateTime, default= datetime.datetime.utcnow)

# Table for unique ids
class Unique_ids(Base):
    __tablename__ = 'Unique_ids'

    id = Column(Integer, primary_key=True, autoincrement=True)

# -----TRIGGERS-----
    # maybe switch to @validate?

# Insert into combined tables triggers
insert_history_lccde = DDL('''\
                           CREATE TRIGGER insert_history_lccde AFTER INSERT ON test_DB.lccde FOR EACH ROW
                           BEGIN
                            INSERT INTO runhistory (run_id, duration, run_date)
                            VALUES (new.run_id, new.duration, new.run_date);
                           END;''')
event.listen(LCCDE.__table__, 'after_create', insert_history_lccde)

insert_history_treebased = DDL('''\
                           CREATE TRIGGER insert_history_treebased AFTER INSERT ON test_DB.treebased FOR EACH ROW
                           BEGIN
                            INSERT INTO runhistory (run_id, duration, run_date)
                            VALUES (new.run_id, new.duration, new.run_date);
                           END;''')
event.listen(TreeBased.__table__, 'after_create', insert_history_treebased)

insert_history_mth = DDL('''\
                           CREATE TRIGGER insert_history_mth AFTER INSERT ON test_DB.mth FOR EACH ROW
                           BEGIN
                            INSERT INTO runhistory (run_id, duration, run_date)
                            VALUES (new.run_id, new.duration, new.run_date);
                           END;''')
event.listen(MTH.__table__, 'after_create', insert_history_mth)

# unique id assignment
lccde_insert_trigger = DDL('''\
                           CREATE TRIGGER lccde_insert_trigger BEFORE INSERT ON lccde FOR EACH ROW
                           BEGIN
                            INSERT INTO unique_ids() VALUES ();
                            SET NEW.run_id = LAST_INSERT_ID();
                           END;''')
event.listen(LCCDE.__table__, 'after_create', lccde_insert_trigger)

treebased_insert_trigger = DDL('''\
                           CREATE TRIGGER treebased_insert_trigger BEFORE INSERT ON treebased FOR EACH ROW
                           BEGIN
                            INSERT INTO unique_ids() VALUES ();
                            SET NEW.run_id = LAST_INSERT_ID();
                           END;''')
event.listen(TreeBased.__table__, 'after_create', treebased_insert_trigger)

mth_insert_trigger = DDL('''\
                           CREATE TRIGGER mth_insert_trigger BEFORE INSERT ON mth FOR EACH ROW
                           BEGIN
                            INSERT INTO unique_ids() VALUES ();
                            SET NEW.run_id = LAST_INSERT_ID();
                           END;''')
event.listen(MTH.__table__, 'after_create', mth_insert_trigger)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session= Session()

session.close()

# TO DO:
    # add items into table and make sure triggers work
    # split whole file into organized classes