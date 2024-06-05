import logging
import inspect
from src.settings import settings
log_to_file = settings.log_to_file
log_file_name = settings.log_filename
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")


ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)


fh = logging.FileHandler(log_file_name)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)


def configure_logger(save_to_file: bool = log_to_file):
    global log_to_file, fh, ch
    log_to_file = save_to_file
    if log_to_file:
        logging.root.addHandler(fh)   
        logging.root.removeHandler(ch)
    else:
        logging.root.addHandler(ch)
        logging.root.removeHandler(fh)


def get_caller_info():
    frame = inspect.currentframe().f_back.f_back
    while frame:
        module_name = inspect.getmodule(frame).__name__
        function_name = frame.f_code.co_name
        if module_name != __name__:
            break
        frame = frame.f_back
    if frame:
        return f"{inspect.getmodule(frame).__name__}.{frame.f_code.co_name}"
    return "unknown"


def setup_logger(level):
    caller_info = get_caller_info()
    logger = logging.getLogger(caller_info)
    logger.setLevel(level)
    return logger


def log_info(msg):
    logger = setup_logger(logging.INFO)
    logger.info(msg)


def log_error(msg):
    logger = setup_logger(logging.ERROR)
    logger.error(msg)


def log_debug(msg):
    logger = setup_logger(logging.DEBUG)
    logger.debug(msg)


configure_logger(save_to_file=log_to_file)
