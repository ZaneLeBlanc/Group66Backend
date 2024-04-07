from data_models import Base
from db_session import engine
from sqlalchemy import event, DDL
from data_models import Base

Base.metadata.create_all(engine)

# Event Triggers
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
