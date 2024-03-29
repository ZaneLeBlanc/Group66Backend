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
    duration = Column(FLOAT)
    run_date = Column(DateTime, default= datetime.datetime.now())
    accuracy = Column(FLOAT)
    prec = Column(FLOAT)
    recall = Column(FLOAT)
    f1_score = Column(FLOAT)
    heatmap_data = Column(String)
    #params
    xgb_n_estimators = Column(Integer)
    xgb_max_depth = Column(Integer)
    xgb_learning_rate = Column(FLOAT)
    lg_num_iterations = Column(Integer)
    lg_max_depth = Column(Integer)
    lg_learning_rate = Column(FLOAT)
    lg_num_leaves = Column(Integer)
    lg_boosting_type = Column(String)
    cb_n_estimators = Column(Integer)
    cb_max_depth = Column(Integer)
    cb_learning_rate = Column(FLOAT)

class TreeBased(Base):
    __tablename__ = 'TreeBased'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(FLOAT)
    run_date = Column(DateTime, default= datetime.datetime.now())
    accuracy = Column(FLOAT)
    prec = Column(FLOAT)
    recall = Column(FLOAT)
    f1_score = Column(FLOAT)

class MTH(Base):
    __tablename__ = 'mth'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(FLOAT) 
    run_date = Column(DateTime, default= datetime.datetime.now())
    accuracy = Column(FLOAT)
    prec = Column(FLOAT)
    recall = Column(FLOAT)
    f1_score = Column(FLOAT)

# Create History table for all runs
        #go back and create link between this table and others
class RunHistory(Base):
    __tablename__ = 'RunHistory'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(Integer, nullable=False)
    run_date = Column(DateTime, default= datetime.datetime.now())
s
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

row = LCCDE(duration = 32.77018928527832, accuracy= 0.9973880597014926, prec= 0.9973952881851091, recall= 0.9973880597014926, f1_score= 0.9973621970126231)
session.add(row)

session.commit()

session.close()

# TO DO:
    # add items into table and make sure triggers work
    # split whole file into organized classes
