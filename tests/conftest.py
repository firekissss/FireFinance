import logging
import os
import tempfile
from unittest.mock import mock_open, MagicMock

import pandas as pd
import pytest


# Fixtures for api_client

@pytest.fixture
def mock_response_success():
    class MockResponse:
        status_code = 200

        def json(self):
            return {"success": True, "data": 123}

        def raise_for_status(self):
            pass

        text = '{"success": true, "data": 123}'

    return MockResponse()


@pytest.fixture
def mock_response_invalid_json():
    class MockResponse:
        status_code = 200

        def json(self):
            raise ValueError("Invalid JSON")

        def raise_for_status(self):
            pass

        text = "<<<invalid>>>"

    return MockResponse()


# Fixtures for decorators.py

@pytest.fixture
def sample_df():
    return pd.DataFrame({"a": [1, 2], "b": [3, 4]})


@pytest.fixture
def mock_os_makedirs(monkeypatch):
    m = MagicMock()
    monkeypatch.setattr(os, "makedirs", m)
    return m


@pytest.fixture
def mock_open_file(monkeypatch):
    m = mock_open()
    monkeypatch.setattr("builtins.open", m)
    return m


@pytest.fixture
def mock_df_to_json(monkeypatch):
    m = MagicMock()
    monkeypatch.setattr(pd.DataFrame, "to_json", m)
    return m


@pytest.fixture
def test_logger_fixture():
    logger = logging.getLogger("test_logger_fixture")
    logger.setLevel(logging.ERROR)

    # очищаем хендлеры, если тесты запускаются многократно
    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)

    return logger


@pytest.fixture
def temp_log_dir():
    """Создаёт временную директорию для логов и возвращает путь"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture()
def cleanup_loggers():
    """Перед и после теста удаляет хендлеры у всех логгеров и очищает GLOBAL_HANDLERS."""
    def clear_all():
        # чистим root
        root = logging.getLogger()
        for h in root.handlers[:]:
            root.removeHandler(h)
            try:
                h.close()
            except:
                pass

        # чистим все зарегистрированные логгеры
        for logger_name, logger in logging.Logger.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):
                for h in logger.handlers[:]:
                    logger.removeHandler(h)
                    try:
                        h.close()
                    except:
                        pass

    # до теста
    clear_all()

    yield

    # после теста
    clear_all()
    # очищаем глобальный список хендлеров (чтобы не тащились в следующую параметризацию)
    try:
        from src import logs  # поправь импорт под свой модуль
        logs.GLOBAL_HANDLERS = []
    except Exception:
        pass