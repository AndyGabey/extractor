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
    from Extractor.models import User, Dataset, Variable, UserToken
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


# Obsolete.
def _export_old():
    from Extractor.models import User, Dataset, Variable, UserToken
    import datetime as dt
    import simplejson
    from glob import glob
    with open('Extractor/import_data/datasets.json', 'r') as f:
        datasets = simplejson.load(f)

    for i, ds in enumerate(datasets):
        ds_dict = mapping[ds['name']]
        new_ds = {}
        relpath_tpl = os.path.join(ds_dict['datadir'], ds_dict['datafile']) 
        newpath_tpl = os.path.join(app.config['DATA_LOCATION'], relpath_tpl)

        new_ds['name'] = ds['name']
        new_ds['long_name'] = ds['longname']
        new_ds['start_date_ts'] = dt.datetime(2016, 1, 1).strftime(DATE_FMT)
        new_ds['end_date_ts'] = dt.datetime(2017, 1, 1).strftime(DATE_FMT)
        new_ds['time_res'] = 86400
        new_ds['file_fmt'] = newpath_tpl

        if 'datetime_fmt' in ds_dict:
            datetime_fmt = ds_dict['datetime_fmt']
        else:
            datetime_fmt = '%Y%m%d %H%M'


        date_col_name = ds_dict['date_col_name']
        if 'time_col_name' in ds_dict:
            time_col_name = ds_dict['time_col_name']
        else:
            time_col_name = ''
        new_ds['date_col_name'] = date_col_name
        new_ds['time_col_name'] = time_col_name
        new_ds['datetime_fmt'] = datetime_fmt

        dataset = Dataset(ds['name'], ds['longname'], dt.datetime(2017, 1, 1), None,
                          5, newpath_tpl, date_col_name , time_col_name, datetime_fmt)

        variables = []
        for var, varlong, vartype in sorted(ds['variables'], key=lambda v: v[1]):
            variable = Variable(var, varlong, '', vartype)
            dataset.variables.append(variable)
            variables.append((var, varlong, vartype))
        new_ds['variables'] = variables

        with open('Extractor/import_data/{0:02d}_dataset_{1}.json'.format(i, new_ds['name']), 'w') as f:
            simplejson.dump(new_ds, f, indent=2)

        #db_session.add(dataset)
    #db_session.commit()
