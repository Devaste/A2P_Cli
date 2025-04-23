import logging

LOG_LEVELS = {
    0: None,           # No logging
    1: logging.ERROR,
    2: logging.WARNING,
    3: logging.INFO,
    4: logging.DEBUG,
}

def configure_logging(level: int, log_file: str = "a2p_cli.log"):
    """
    Configure logging for the application.
    level: integer 0-4 (0 disables logging, 1=ERROR, 2=WARNING, 3=INFO, 4=DEBUG)
    If level is 0, disables logging and does not create a log file.
    Uses force=True to ensure robust configuration in all environments.
    Explicitly sets handler levels for reliability.
    """
    if level <= 0:
        logging.disable(logging.CRITICAL)
        return
    logging.basicConfig(
        level=LOG_LEVELS.get(level, logging.ERROR),
        format="%(asctime)s [%(levelname)s] %(message)s",
        filename=log_file,
        filemode="w",
        force=True  # Always reconfigure handlers
    )
    log_level = LOG_LEVELS.get(level, logging.ERROR)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers:
        handler.setLevel(log_level)
