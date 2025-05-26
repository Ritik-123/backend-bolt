import os, datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(BASE_DIR, 'logs')
ARC_DIR= os.path.join(BASE_DIR, 'archive')

os.makedirs(LOG_DIR, exist_ok= True)
os.makedirs(ARC_DIR, exist_ok= True)

LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {lineno} {module} {funcName} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        
        'server_logs': {
            "level": "INFO",
            'class': 'concurrent_log_handler.ConcurrentTimedRotatingFileHandler',
            # 'when': 'm',
            # 'interval': 3,
            'when': 'midnight',
            "atTime": datetime.time(23, 57, 00),
            'filename': os.path.join(LOG_DIR, 'server.log'),
            "formatter": "verbose",
        },

        'access_logs': {
            "level": "INFO",
            'class': 'concurrent_log_handler.ConcurrentTimedRotatingFileHandler',
            'when': 'midnight',
            "atTime": datetime.time(23, 57, 00),
            'filename': os.path.join(LOG_DIR, 'access.log'),
            "formatter": "verbose",
        }
    },

    'loggers': {

        'server': {
            'handlers': ['server_logs'],
            'level': 'INFO',
            'propagate': False,
        },

        'access': {
            'handlers': ['access_logs'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}