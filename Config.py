import logging
import logging.config
from datetime import datetime
Config = {
    'logging' : {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s: %(levelname)s,[%(name)s],%(message)s',
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                #'filename': 'sugarscape.log',
                'filename': 'sugarscape_%s.log' % datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'),
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
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
