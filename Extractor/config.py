class Config(object):
    DEBUG = False
    TESTING = False
    DATA_LOCATION = 'demo_data'
    DB_NAME = 'db/extractor.db'


class ProductionConfig(Config):
    DATA_LOCATION = '/mnt/data/metfidas'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
