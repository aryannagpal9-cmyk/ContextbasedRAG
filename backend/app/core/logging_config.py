import logging
import sys

def setup_logging():
    """
    Configures centralized logging for the application.
    - Level: INFO
    - Format: Structured with timestamp and level
    - Output: Stdout for container compatibility
    """
    logger = logging.getLogger("ultra_doc_intel")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Console Handler
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Singleton-like access
logger = setup_logging()
