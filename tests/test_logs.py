import logging
import sys

import pytest

from src import logs
from logging.handlers import RotatingFileHandler


@pytest.mark.parametrize("enable_file, enable_console", [
    (True, False),
    (False, True),
    (True, True)
])
@pytest.mark.parametrize("level", [logging.DEBUG, logging.INFO, logging.WARNING])
def test_setup_logging_unique_logger(temp_log_dir, cleanup_loggers, enable_file, enable_console, level):
    logger_name = f"i_spent_6_hours_on_this_test"

    logs.setup_logging(
        level=level,
        enable_file=enable_file,
        enable_console=enable_console,
        log_dir=temp_log_dir
    )

    logger = logs.get_logger(logger_name)
    assert logger.name == logger_name

    file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    console_handlers = [h for h in logger.handlers
                        if isinstance(h, logging.StreamHandler) and getattr(h, 'stream', None) == sys.stdout]
    # интересный факт, строчка выше
    # RotatingFileHandler наследуется от FileHandler -> StreamHandler
    # до меня дошло через 6 часов посмотреть откуда наследуется этот класс
    # спасибо за внимание

    if enable_file:
        assert len(file_handlers) == 1
    else:
        assert len(file_handlers) == 0

    if enable_console:
        assert len(console_handlers) == 1
    else:
        assert len(console_handlers) == 0


def test_get_logger_instance(cleanup_loggers):
    name = "my_test_logger"
    logger = logs.get_logger(name)
    assert isinstance(logger, logging.Logger)
    assert logger.name == name


def test_setup_logging_removes_existing_handlers(temp_log_dir, cleanup_loggers):
    # Первый вызов
    logs.setup_logging(enable_file=True, log_dir=temp_log_dir)
    root_logger = logging.getLogger()
    first_handlers = list(root_logger.handlers)

    # Второй вызов должен очистить старые хендлеры
    logs.setup_logging(enable_file=True, log_dir=temp_log_dir)
    new_handlers = list(root_logger.handlers)

    # Должны быть новые объекты, не старые
    assert first_handlers != new_handlers

    # Старые хендлеры закрыты
    for h in first_handlers:
        if hasattr(h, "stream") and h.stream:
            assert h.stream.closed or isinstance(h, RotatingFileHandler)


def test_log_file_rotation_settings(temp_log_dir, cleanup_loggers):
    max_bytes = 1024
    backup_count = 3
    logs.setup_logging(enable_file=True, log_dir=temp_log_dir, max_bytes=max_bytes, backup_count=backup_count)
    root_logger = logging.getLogger()
    fh = next((h for h in root_logger.handlers if isinstance(h, RotatingFileHandler)), None)
    assert fh is not None
    assert fh.maxBytes == max_bytes
    assert fh.backupCount == backup_count
