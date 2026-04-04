import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


class RelativePathFormatter(logging.Formatter):
    """Custom formatter that shows relative file paths and milliseconds for time."""

    def format(self, record):
        # Get relative path from ROOT_DIR
        try:
            record.relpath = str(Path(record.pathname).relative_to(settings.ROOT_DIR))
        except ValueError:
            record.relpath = record.pathname

        # Format the log message
        return super().format(record)


def setup_logging() -> None:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Create logs directory if it doesn't exist
    logs_dir = settings.ROOT_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_format = "%(levelname)s | %(asctime)s.%(msecs)03d | %(relpath)s: %(message)s"

    def create_formatter():
        formatter = RelativePathFormatter(log_format, datefmt="%H:%M:%S")
        return formatter

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(create_formatter())
    root_logger.addHandler(console_handler)

    # Application log file handler
    app_log_file = logs_dir / "application.log"
    app_file_handler = RotatingFileHandler(
        app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    app_file_handler.setFormatter(create_formatter())
    root_logger.addHandler(app_file_handler)

    # Error log file handler
    error_log_file = logs_dir / "application-error.log"
    error_file_handler = RotatingFileHandler(
        error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    error_file_handler.setFormatter(create_formatter())
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)

    logger = logging.getLogger("cloud-companion")
    logger.debug(f"Logging configured with level: {settings.LOG_LEVEL}")


def get_logger(name: str = "cloud-companion") -> logging.Logger:
    return logging.getLogger(name)
