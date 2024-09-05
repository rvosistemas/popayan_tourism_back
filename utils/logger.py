# logger_config.py
import logging
from colorlog import ColoredFormatter


def configure_logger() -> logging.Logger:
    logger = logging.getLogger("popayan_tourism_backend_app")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s:%(name)s:%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


app_logger = configure_logger()
