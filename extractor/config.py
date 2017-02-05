class Config(object):
    DEBUG = False
    TESTING = False
    DATA_LOCATION = 'demo_data/metfidas'
    DB_LOCATION = 'sqlite:////tmp/extractor.db'


class ProductionConfig(Config):
    DATA_LOCATION = '/mnt/data/metfidas'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
