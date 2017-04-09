import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Extractor import app
from Extractor.utils import DATE_FMT

db_string = 'sqlite:///' + os.path.join(app.root_path, app.config['DB_NAME'])
engine = create_engine(db_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db(drop_all=True, populate=True, import_data=True):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import Extractor.models
    if drop_all:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    if populate:
        populate_db()
    if import_data:
        import_datasets()


def populate_db(delete_all=False):
    from Extractor.models import User, Dataset, Variable, UserToken

    if delete_all:
        User.query.delete()
        Dataset.query.delete()
        Variable.query.delete()
        UserToken.query.delete()

    user = User('Mark', 'markmuetz@gmail.com', 'dummypw')
    db_session.add(user)


def import_datasets():
    from Extractor.models import Dataset, Variable
    import datetime as dt
    import simplejson
    from glob import glob
    for filename in sorted(glob('Extractor/import_data/??_dataset_*.json')):
        print(filename)
        with open(filename, 'r') as f:
            dataset_args = simplejson.load(f)

        variables = dataset_args.pop('variables')
        dataset_args['start_date'] = dt.datetime.strptime(dataset_args.pop('start_date_ts'),
                                                          DATE_FMT)
        dataset_args['end_date'] = dt.datetime.strptime(dataset_args.pop('end_date_ts'),
                                                        DATE_FMT)

        dataset = Dataset(**dataset_args)

        for var, varlong, vartype in sorted(variables, key=lambda v: v[1]):
            variable = Variable(var, varlong, '', vartype)
            dataset.variables.append(variable)
        db_session.add(dataset)
    db_session.commit()
