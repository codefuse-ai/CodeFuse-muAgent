import logging
from loguru import logger as loguru_logger


def get_logger():
    return loguru_logger

    FORMAT = '[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    logger_loggering = logging.getLogger()
    return logger_loggering

import os
if os.environ.get("operation_mode")=="antcode":
    import logging
    FORMAT = '[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
else:
    from loguru import logger as logging


if __name__ == '__main__':
    logger = get_logger()
    logger.info('hjaha')