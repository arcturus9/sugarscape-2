import logging
import logging.config
from datetime import datetime
Config = {
    'logging' : {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '%(asctime)s:%(module)s,%(lineno)s,%(levelname)s,[%(name)s],%(message)s',
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'sugarscape_%s.log' % datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'),
                'formatter': 'standard',
                'mode': 'a',
                'maxBytes': 104857600,
                'backupCount': 5,
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default',],
                'level': 'DEBUG',
                'formatter': 'standard',
                'propagate': True,
            },
        },
    },
    'dbHost': '127.0.0.1',
    'dbBucket': 'default',
    'consumeRate': 1,
}

logging.config.dictConfig(Config['logging'])
