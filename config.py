import os

class config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    THREADED = True
    PORT = int(os.environ.get('PORT', 5001))
    # This shouldn't be visible
    SECRET_KEY = '\xe3\xa3\xecK>\x82\xc1\xdfH=\xd0S\xb3\x9eX\x97\xfd\xeb\xefO\xdf\xda\x10\x96'


class ProductionConfig(config):
    DEBUG = False


class StagingConfig(config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(config):
    TESTING = True