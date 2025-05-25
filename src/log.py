import logging
import os


def change_extension(file_path, new_extension):
    return os.path.splitext(file_path)[0] + new_extension


def set_up_main_logger(log_path,
                       stdout_log_level=logging.DEBUG,
                       file_log_level=logging.DEBUG):
    DEFAULT_STYLE = "{"  # use f-string like interpolation in formatting
    DEFAULT_FORMAT = "[{asctime}][{name}][{levelname}] {message}"
    DEFAULT_DATE_FORMAT = "%m/%d %H:%M:%S"

    DEFAULT_FORMATTER = logging.Formatter(fmt=DEFAULT_FORMAT,
                                          datefmt=DEFAULT_DATE_FORMAT,
                                          style=DEFAULT_STYLE,
                                          validate=True,
                                          defaults=None)

    logging.basicConfig(
        level=stdout_log_level,
        style=DEFAULT_STYLE,
        datefmt=DEFAULT_DATE_FORMAT,
        format=DEFAULT_FORMAT,
    )

    file_handler = logging.FileHandler(log_path,
                                       mode='a',
                                       encoding="utf-8",
                                       delay=True,
                                       errors=None)
    file_handler.setFormatter(DEFAULT_FORMATTER)
    file_handler.setLevel(file_log_level)

    # Add file sink to root logger.
    logging.getLogger().addHandler(file_handler)
