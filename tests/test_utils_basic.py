import pytest
import json
from datetime import datetime
from unittest.mock import mock_open

from src.utils import (
    print_banner,
    load_user_settings,
    get_user_currencies,
    get_user_stocks,
    get_greeting_by_current_time,
    get_date_interval,
)


def test_print_banner(monkeypatch):
    fake_banner = "FAKE BANNER"
    fake_path = "banner.txt"

    # подмена open
    m = mock_open(read_data=fake_banner)
    monkeypatch.setattr("builtins.open", m)

    printed = []
    monkeypatch.setattr("builtins.print", lambda x: printed.append(x))

    print_banner(fake_path)

    m.assert_called_once_with(fake_path, "r", encoding="utf-8")
    assert printed == [fake_banner]


def test_load_user_settings(monkeypatch):
    fake_json = {"a": 1}
    fake_path = "settings.json"

    m = mock_open(read_data=json.dumps(fake_json))
    monkeypatch.setattr("builtins.open", m)

    result = load_user_settings(fake_path)

    assert result == fake_json
    m.assert_called_once_with(fake_path, "r", encoding="utf-8")


def test_get_user_currencies(monkeypatch):
    fake_settings = {"user_currencies": ["USD", "EUR"]}

    monkeypatch.setattr("src.utils.load_user_settings", lambda _: fake_settings)

    result = get_user_currencies("path")
    assert result == ["USD", "EUR"]


def test_get_user_stocks(monkeypatch):
    fake_settings = {"user_stocks": ["AAPL", "TSLA"]}

    monkeypatch.setattr("src.utils.load_user_settings", lambda _: fake_settings)

    result = get_user_stocks("path")
    assert result == ["AAPL", "TSLA"]


@pytest.mark.parametrize("hour,expected", [
    (7, "Доброе утро"),
    (13, "Добрый день"),
    (19, "Добрый вечер"),
    (2, "Доброй ночи"),
])
def test_get_greeting_by_current_time(hour, expected, monkeypatch):
    class FakeDT:
        @classmethod
        def now(cls):
            return datetime(2024, 1, 1, hour, 0, 0)

    monkeypatch.setattr("src.utils.datetime", FakeDT)

    assert get_greeting_by_current_time() == expected


def test_get_date_interval():
    dt = datetime(2023, 5, 17, 14, 30)
    start, end = get_date_interval(dt)

    assert end == dt
    assert start == datetime(2023, 5, 1, 0, 0, 0)
