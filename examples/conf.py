import logging as log
import os

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logger.log',
            'encoding': 'utf8',
            'maxBytes': 100000,
            'backupCount': 1,
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'db'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# Wait before next action
SLEEP_TIME = 1

