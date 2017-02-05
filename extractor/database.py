from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:////tmp/extractor.db', convert_unicode=True)
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
        user = extractor.models.User('Mark', 'markmuetz@gmail.com', 'dummypw')
        db_session.add(user)

        ds = extractor.models.Dataset(dt.datetime(2017, 1, 1), dt.datetime.now(),
                                      5, 'AWS', 'PrecipMaster3000', 
                                      '/some/file/path/{year}/', 
                                      'TimeStamp' , '%d%m', 'Time', '%s')
        db_session.add(ds)
        db_session.commit()

