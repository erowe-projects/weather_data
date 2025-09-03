import logging

def get_logger(name: str) -> logging.Logger:
    """
    Get a preconfigured logger for the package.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # prevent duplicate handlers
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

