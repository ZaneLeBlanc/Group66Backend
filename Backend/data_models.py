from sqlalchemy import Column, Integer, String, DateTime, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import FLOAT
import datetime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class LCCDE(Base):
    __tablename__ = 'LCCDE'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    run_date = Column(DateTime, default= datetime.datetime.now())
    dataset_path = Column(String)
    duration = Column(FLOAT)
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
    run_date = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(FLOAT)
    accuracy = Column(FLOAT)
    prec = Column(FLOAT)
    recall = Column(FLOAT)
    f1_score = Column(FLOAT)
    heatmap_data = Column(String)

    #parameters
    xgb_estimators = Column(FLOAT)
    xgb_max_depth = Column(Integer)
    xgb_learning_rate = Column(FLOAT)
    dtree_max_depth = Column(Integer)
    dtree_min_samples = Column(FLOAT)
    dtree_splitter = Column(String)
    rtree_estimators = Column(Integer)
    rtree_max_depth = Column(Integer)
    rtree_min_samples = Column(FLOAT)
    etree_estimators = Column(Integer)
    etree_max_depth = Column(Integer)
    etree_min_samples = Column(FLOAT)
    # tree_criterion = Column(String)

class MTH(Base):
    __tablename__ = 'mth'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    run_date = Column(DateTime, default= datetime.datetime.now())
    dataset_path = Column(String)
    duration = Column(FLOAT)
    accuracy = Column(FLOAT)
    prec = Column(FLOAT)
    recall = Column(FLOAT)
    f1_score = Column(FLOAT)
    heatmap_data = Column(String)
    #params
    train_split = Column(FLOAT)
    max_features = Column(Integer)
    hpo_max_evals = Column(Integer)

# Create History table for all runs
        #go back and create link between this table and others
class RunHistory(Base):
    __tablename__ = 'RunHistory'

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(Integer, nullable=False)
    run_date = Column(DateTime, default= datetime.datetime.now())