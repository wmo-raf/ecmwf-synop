import logging
import os

log_level = logging.getLevelName(os.getenv('LOG', "INFO"))

SETTINGS = {
    'logging': {
        'level': log_level
    },
    'service': {
        'port': os.getenv('PORT')
    },
    'SQLALCHEMY_DATABASE_URI': os.getenv('SQLALCHEMY_DATABASE_URI'),
    'STATE_DIR': os.getenv('STATE_DIR'),
    'DATASETS_DIR': os.getenv('DATASETS_DIR'),
    'ITEMS_PER_PAGE': int(os.getenv('ITEMS_PER_PAGE', 20)),
    'UPLOAD_FOLDER': '/tmp/datasets',
    'ROLLBAR_SERVER_TOKEN': os.getenv('ROLLBAR_SERVER_TOKEN'),
    'PG_SERVICE_SCHEMA': os.getenv('PG_SERVICE_SCHEMA', "pgadapter"),
    'PG_SERVICE_USER': os.getenv('PG_SERVICE_USER'),
    'PG_SERVICE_USER_PASSWORD': os.getenv('PG_SERVICE_USER_PASSWORD'),
    'GRAYLOG_HOST': os.getenv('GRAYLOG_HOST'),
    'GRAYLOG_PORT': os.getenv('GRAYLOG_PORT'),
    'API_USERNAME': os.getenv('API_USERNAME'),
    'API_PASSWORD_HASH': os.getenv('API_PASSWORD_HASH'),
}
