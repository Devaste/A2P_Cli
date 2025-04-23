import logging

def test_file_logging_at_error_level(tmp_path):
    log_file = tmp_path / "test.log"
    logger = logging.getLogger("a2p_cli_test_logger")
    logger.handlers.clear()
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
    formatter = logging.Formatter("%(levelname)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.error("Error message")
    logger.warning("Warning message")
    logger.info("Info message")
    logger.debug("Debug message")

    handler.flush()
    handler.close()
    logger.handlers.clear()

    assert log_file.exists()
    with open(log_file, encoding="utf-8") as f:
        lines = f.read()
    assert "Error message" in lines
    assert "Warning message" not in lines
    assert "Info message" not in lines
    assert "Debug message" not in lines

def test_file_logging_at_debug_level(tmp_path):
    log_file = tmp_path / "test.log"
    logger = logging.getLogger("a2p_cli_test_logger")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
    formatter = logging.Formatter("%(levelname)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.debug("Debug message")

    handler.flush()
    handler.close()
    logger.handlers.clear()

    assert log_file.exists()
    with open(log_file, encoding="utf-8") as f:
        lines = f.read()
    assert "Debug message" in lines
