import logging
import os

from core.services.path_manager import PathManager

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
ERROR_LOG_FILE = 'flowdeck_errors.log'


def get_log_directory():
    root_dir = PathManager.get_root_dir()
    log_dir = os.path.join(root_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def setup_logging():
    """Initialize a centralized logging configuration for the whole application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear any preexisting handlers to avoid duplicate logs.
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    log_dir = get_log_directory()

    error_log_path = os.path.join(log_dir, ERROR_LOG_FILE)
    error_handler = logging.FileHandler(error_log_path, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    root_logger.debug(f'Logging initialized. Error log: {error_log_path}')
    return root_logger
