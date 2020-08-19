import logging
import os
import threading

initLock = threading.Lock()
rootLoggerInitialized = False
log_format = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
logger_dict = {}
global_config = None

LOGGER_ROOT = 'root'
LOGGER_STRATEGY = 'strategy'
LOGGER_SYSTEM = 'system'
LOGGER_FRAME = 'frame'
LOGGER_TICK = 'tick'


def initialize(logger_name, config=None):
    global logger_dict
    with initLock:
        if logger_name not in logger_dict:
            l = logging.getLogger(logger_name)
            if config is not None:
                global global_config
                global_config = config
                setup_config_logger(config, logger_name, l)
            elif global_config is not None:
                setup_config_logger(global_config, logger_name, l)
            else:
                setup_console_logger(l, logging.INFO)
            set_logger(logger_name, l)


def setup_config_logger(config, logger_name, l):
    if 'logMode' in config:
        log_mode = config['logMode']
    else:
        log_mode = 'console'
    log_level = config['logLevel']
    if log_mode == 'file':
        setup_file_logger(l, config, logger_name, log_level)
    else:
        setup_console_logger(l, log_level)


def setup_file_logger(l, config, logger_name, log_level):
    log_path = config['logPath']
    if os.path.exists(log_path):
        pass
    else:
        os.makedirs(log_path)
    log_suffix = config['logSuffix']
    log_format = config['logFormat']
    log_file = log_path + logger_name + log_suffix
    if not l.handlers:
        fileHandler = logging.FileHandler(log_file, mode='a')
        init_handler(fileHandler, log_format)
        l.setLevel(log_level)
        l.addHandler(fileHandler)


def setup_console_logger(logger, log_level):
    logger.setLevel(log_level)
    consoleHandler = logging.StreamHandler()
    init_handler(consoleHandler)
    logger.addHandler(consoleHandler)


def init_handler(handler, fmt=log_format):
    handler.setFormatter(Formatter(fmt))


def set_logger(logger_name, l):
    if LOGGER_STRATEGY in logger_name:
        logger_dict[LOGGER_STRATEGY] = l
    elif LOGGER_SYSTEM in logger_name:
        logger_dict[LOGGER_SYSTEM] = l
        logger_dict[LOGGER_ROOT] = l
    elif LOGGER_FRAME in logger_name:
        logger_dict[LOGGER_FRAME] = l
    elif LOGGER_TICK in logger_name:
        logger_dict[LOGGER_TICK] = l
    else:
        logger_dict[LOGGER_ROOT] = l


def get_name(logger_name):
    if LOGGER_STRATEGY in logger_name:
        name = LOGGER_STRATEGY
    elif LOGGER_SYSTEM in logger_name:
        name = LOGGER_SYSTEM
    elif LOGGER_FRAME in logger_name:
        name = LOGGER_FRAME
    elif LOGGER_TICK in logger_name:
        name = LOGGER_TICK
    else:
        name = LOGGER_ROOT
    return name


def getLogger(name=None):
    if name is None:
        name = LOGGER_ROOT
    else:
        name = get_name(name)
    return logger_dict[name]


# This formatter provides a way to hook in formatTime.
class Formatter(logging.Formatter):
    DATETIME_HOOK = None

    def formatTime(self, record, datefmt=None):
        newDateTime = None

        if Formatter.DATETIME_HOOK is not None:
            newDateTime = Formatter.DATETIME_HOOK()

        if newDateTime is None:
            ret = super(Formatter, self).formatTime(record, datefmt)
        else:
            ret = str(newDateTime)
        return ret
