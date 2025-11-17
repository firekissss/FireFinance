import logging

import pandas as pd
import pytest
from src.decorators import report_to_file, log_exceptions


#       report_to_file()

def test_report_to_file_dataframe(mock_os_makedirs, mock_df_to_json, sample_df, monkeypatch):
    monkeypatch.setattr("builtins.print", lambda *a, **kw: None)

    @report_to_file("test_report.json")
    def dummy():
        return sample_df

    result = dummy()

    assert isinstance(result, pd.DataFrame)
    mock_os_makedirs.assert_called_once()
    mock_df_to_json.assert_called_once()


def test_report_to_file_dict(mock_os_makedirs, mock_open_file, monkeypatch):
    monkeypatch.setattr("builtins.print", lambda *a, **kw: None)

    @report_to_file("test_report.json")
    def dummy():
        return {"x": 1}

    result = dummy()

    assert result == {"x": 1}
    mock_os_makedirs.assert_called_once()
    mock_open_file.assert_called_once()


def test_report_to_file_default_filename(mock_os_makedirs, mock_df_to_json, sample_df, monkeypatch):
    monkeypatch.setattr("builtins.print", lambda *a, **kw: None)

    @report_to_file()
    def dummy():
        return sample_df

    result = dummy()

    assert isinstance(result, pd.DataFrame)
    mock_df_to_json.assert_called_once()


#       log_exceptions()

def test_log_exceptions_no_error(test_logger_fixture):
    @log_exceptions(test_logger_fixture)
    def ok_func():
        return 10

    assert ok_func() == 10


def test_log_exceptions_catches_exception(test_logger_fixture, caplog):
    @log_exceptions(test_logger_fixture)
    def bad_func():
        raise ValueError("something")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            bad_func()

    assert "something" in caplog.text

    # в консоли при запуске Pytest появляется ожидаемое исключение.
    # это никак не убрать при текущей конфигурации теста
    # но тест проходит успешно
