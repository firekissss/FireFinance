import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "app.log"


def setup_logging(
        level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB per file
        backup_count: int = 5,
        enable_console: bool = False,
        enable_file: bool = True,
        log_dir: Optional[str] = None
) -> None:
    """
    Initializes global logging configuration for the entire project.

    This function should be called once at the application startup (e.g., in main.py).
    It sets up file logging with rotation and optional console output.

    Parameters
    ----------
    level : int, optional
        Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING).
        Default is logging.INFO.
    max_bytes : int, optional
        Maximum size of log file in bytes before rotation occurs.
        Default is 10 MB.
    backup_count : int, optional
        Number of backup log files to keep when rotating.
        Default is 5.
    enable_console : bool, optional
        Whether to enable console output for logs.
        Default is False.
    enable_file : bool, optional
        Whether to enable file logging.
        Default is True.
    log_dir : str or None, optional
        Custom directory for log files. If None, uses 'logs' directory in project root.
        Default is None.

    Returns
    -------
    None
    """
    # Определяем директорию для логов
    if log_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(base_dir, LOG_DIR_NAME)

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, LOG_FILE_NAME)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
    )

    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Очищаем существующие хендлеры (на случай повторного вызова)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # File handler (с ротацией)
    if enable_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance for the specified name.

    This function should be used in modules to get a logger that follows
    the project's logging configuration.

    Parameters
    ----------
    name : str
        Name of the logger, typically __name__ of the module.

    Returns
    -------
    logging.Logger
        Configured logger instance ready for use.
    """
    return logging.getLogger(name)
