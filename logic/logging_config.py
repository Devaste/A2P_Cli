import logging
import os

LOG_LEVELS = {
    0: None,           # No logging
    1: logging.CRITICAL,
    2: logging.ERROR,
    3: logging.WARNING,
    4: logging.DEBUG,
}

def configure_logging(level=4, log_file='a2pcli_debug.log'):
    """
    Configure logging for the application.
    level: integer 0-4 (0 disables logging, 1=CRITICAL, 2=ERROR, 3=WARNING, 4=DEBUG)
    If level is 0, disables logging and does not create a log file.
    Uses force=True to ensure robust configuration in all environments.
    Explicitly sets handler levels for reliability.
    """
    logging.disable(logging.NOTSET)  # Re-enable logging globally
    log_level = LOG_LEVELS.get(level, logging.ERROR)
    if log_level is None:
        logging.disable(logging.CRITICAL)
        return
    if log_file:
        os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            filename=log_file,
            filemode="w",
            force=True  # Always reconfigure handlers
        )
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers:
        handler.setLevel(log_level)
    logging.getLogger().addHandler(logging.StreamHandler())  # Optional: also log to stdout
