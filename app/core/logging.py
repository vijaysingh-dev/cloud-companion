import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.constants import AppMode
from app.core.config import settings

_configured = False


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


def setup_logging(mode: AppMode = AppMode.APP) -> None:
    """Configure root logging once per process. File output is split by entrypoint (AppMode)."""
    global _configured
    if _configured:
        return
    _configured = True

    context = mode.value.lower()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logs_dir = settings.ROOT_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_format = "%(levelname)s | %(asctime)s.%(msecs)03d | %(relpath)s: %(message)s"

    def create_formatter():
        return RelativePathFormatter(log_format, datefmt="%H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(create_formatter())
    root_logger.addHandler(console_handler)

    app_log_file = logs_dir / f"{context}.log"
    app_file_handler = RotatingFileHandler(app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    app_file_handler.setFormatter(create_formatter())
    root_logger.addHandler(app_file_handler)

    error_log_file = logs_dir / f"{context}-error.log"
    error_file_handler = RotatingFileHandler(
        error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    error_file_handler.setFormatter(create_formatter())
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)

    logging.getLogger("cloud-companion").debug(
        f"Logging configured (context={context}, level={settings.LOG_LEVEL})"
    )
