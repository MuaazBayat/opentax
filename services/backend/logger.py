"""
Centralized logging configuration using Loguru.
Provides structured logging with different levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
"""
from loguru import logger
import sys
import os

# Remove default handler
logger.remove()

# Get log level from environment variable, default to DEBUG
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

# Add console handler with colored output
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True,
)

# Add file handler for all logs
logger.add(
    "logs/app.log",
    rotation="500 MB",  # Rotate when file reaches 500 MB
    retention="10 days",  # Keep logs for 10 days
    compression="zip",  # Compress rotated logs
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    enqueue=True,  # Thread-safe logging
)

# Add separate file handler for errors only
logger.add(
    "logs/errors.log",
    rotation="100 MB",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    enqueue=True,
)

# Add JSON file handler for structured logging (useful for log aggregation)
logger.add(
    "logs/app.json",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    serialize=True,  # JSON format
    level="INFO",
    enqueue=True,
)

def get_logger(name: str):
    """
    Get a logger instance with a specific name.

    Usage:
        from logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is an info message")
        logger.error("This is an error", extra={"context": "value"})
    """
    return logger.bind(name=name)

# Export the logger
__all__ = ["logger", "get_logger"]
