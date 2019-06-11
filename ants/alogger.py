# -*- coding: utf-8 -*-
import logging
import logging.config
import ants.utils as utils
import os
import json

# https://python-guide-kr.readthedocs.io/ko/latest/writing/logging.html
# https://www.python.org/dev/peps/pep-0391/
# https://docs.djangoproject.com/en/2.1/topics/logging/
# https://stackoverflow.com/questions/38537905/set-logging-levels

# format 참고
# '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s'

DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s",
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple"
        },
        "file":{
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "backupCount": 31,
            "level": "DEBUG",
            "formatter": "default",
            "filename" : "logs/ants.log",
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "__main__": {
            "handlers": ["console","file"],
            "level": "INFO",
        },
        "TEST_CLASS_NAME": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
    "root":{
        "handlers": ["console","file"],
        "level": "DEBUG",
    }
}



#The log settings are read from the file
#If there is no setting, follow the default setting.

logging.basicConfig()
try:
    with open("configs/log.conf", "r") as fd:
        logging.config.dictConfig(json.load(fd))
except Exception as ex:
    print(ex)
    print("Can't load log.conf file")
    logging.config.dictConfig(DEFAULT_CONFIG)
    pass

logger = logging.getLogger()  # Returns the "root" logger
print(logger.getEffectiveLevel())  # Check what level of messages will be shown


if __name__ == "__main__":
    logger = logging.getLogger("__main__")
    print("...?")
    logging.info("Program Start")
    logging.debug("debug log")
    print("...?")
    print("...?")
    

# logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# stream_hander = logging.StreamHandler()
# stream_hander.setFormatter(formatter)
# logger.addHandler(stream_hander)

# file_handler = logging.FileHandler("./logs/ants.log")
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

