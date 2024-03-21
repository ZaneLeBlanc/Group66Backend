from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy import event, DDL
from sqlalchemy.dialects.mysql import FLOAT
from sqlalchemy.orm import declarative_base
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

# -----TRIGGERS-----
    # maybe switch to @validate?
@event.listens_for(Base.metadata, 'after_create')
def make_triggers(target, connection, **kw):
    t_ddls = [
        DDL('''\
                           CREATE TRIGGER lccde_insert_trigger AFTER INSERT ON lccde FOR EACH ROW
                           BEGIN
                            INSERT INTO runhistory (run_id, duration, run_date) VALUES (NULL,  new.duration, new.run_date);
                            UPDATE lccde SET run_id = (SELECT last_insert_rowid()) WHERE rowid = NEW.rowid;
                           END;'''),
        DDL('''\
                           CREATE TRIGGER treebased_insert_trigger AFTER INSERT ON treebased FOR EACH ROW
                           BEGIN
                            INSERT INTO runhistory (run_id, duration, run_date) VALUES (NULL,  new.duration, new.run_date);
                            UPDATE treebased SET run_id = (SELECT last_insert_rowid()) WHERE rowid = NEW.rowid;
                           END;'''),
        DDL('''\
                           CREATE TRIGGER mth_insert_trigger AFTER INSERT ON mth FOR EACH ROW
                           BEGIN
                            INSERT INTO runhistory (run_id, duration, run_date) VALUES (NULL,  new.duration, new.run_date);
                            UPDATE mth SET run_id = (SELECT last_insert_rowid()) WHERE rowid = NEW.rowid;
                           END;''')
    ]

    for ddl in t_ddls:
        connection.execute(ddl)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session= Session()

tb = LCCDE(duration = '00:01:11', accuracy='0.222222', prec='0.444444' ,recall='0.555555', f1_score='0.999999' )
session.add(tb)
session.commit()
tb = MTH(duration = '00:44:11', accuracy='0.222222', prec='0.444444' ,recall='0.555555', f1_score='0.999999' )
session.add(tb)
session.commit()
tb = TreeBased(duration = '00:01:14', accuracy='0.222222', prec='0.444444' ,recall='0.555555', f1_score='0.999999' )
session.add(tb)
session.commit()

session.close()

# TO DO:
    # add items into table and make sure triggers work
    # split whole file into organized classes