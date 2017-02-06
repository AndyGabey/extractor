import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from extractor import app


engine = create_engine(app.config['DB_LOCATION'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db(populate=False):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import extractor.models
    Base.metadata.create_all(bind=engine)

    if populate:
        import datetime as dt
        import simplejson

        user = extractor.models.User('Mark', 'markmuetz@gmail.com', 'dummypw')
        db_session.add(user)

        with open('extractor/import_data/datasets.json', 'r') as f:
            datasets = simplejson.load(f)
        for ds in datasets:
            dataset = extractor.models.Dataset(ds['name'], ds['longname'], dt.datetime(2017, 1, 1), dt.datetime.now(),
                                               5, 'instrument', 
                                               '/some/file/path/{year}/', 
                                               'TimeStamp' , '%d%m', 'Time', '%s')
            for var, varlong, vartype in ds['variables']:
                variable = extractor.models.Variable(var, varlong, '', vartype)
                dataset.variables.append(variable)
            db_session.add(dataset)
        db_session.commit()

