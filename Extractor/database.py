import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Extractor import app

db_string = 'sqlite:///' + os.path.join(app.root_path, app.config['DB_NAME'])
engine = create_engine(db_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db(drop_all=False, populate=False):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import Extractor.models
    if drop_all:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    if populate:
        populate_db()


def populate_db(delete_all=False):
    import datetime as dt
    import simplejson

    from Extractor.models import User, Dataset, Variable, UserToken

    if delete_all:
        User.query.delete()
        Dataset.query.delete()
        Variable.query.delete()
        UserToken.query.delete()

    user = User('Mark', 'markmuetz@gmail.com', 'dummypw')
    db_session.add(user)

    with open('Extractor/import_data/datasets.json', 'r') as f:
        datasets = simplejson.load(f)

    for ds in datasets:
        path_tpl = os.path.join(ds['datadirs'][-1], ds['datafile'])
        relpath_tpl = os.path.relpath(path_tpl, '/export/its/labs')
        newpath_tpl = os.path.join(app.config['DATA_LOCATION'], 'Extractor', relpath_tpl)
        print(path_tpl)
        print(relpath_tpl)
        print(newpath_tpl)
        level = 0
        if 'Level1' in newpath_tpl:
            level = 1
        elif 'Level2' in newpath_tpl:
            level = 2
        dataset = Dataset(ds['name'], ds['longname'], dt.datetime(2017, 1, 1), None,
                          5, 'instrument', level, newpath_tpl, 
                          'TimeStamp' , '%d%m', 'Time', '%s')
        for var, varlong, vartype in sorted(ds['variables'], key=lambda v: v[1]):
            variable = Variable(var, varlong, '', vartype)
            dataset.variables.append(variable)
        db_session.add(dataset)
    db_session.commit()
