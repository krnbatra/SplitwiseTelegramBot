import logging


def init_logger(logfile: str):
    """Initialize the root logger and standard log handlers."""
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


def get_logger(name: str = None):
    """Provide the root logger or initialize new."""
    return logging.getLogger(name)


def print_app_log(logger, update, message):
    username = update.effective_user.username
    name = update.effective_user.first_name

    if username is not None:
        name_details = f"@{username} {name}"
    else:
        name_details = f"{name}"
    logger.info(
        f"APP, {name_details}, {message}")
