from unittest.mock import MagicMock, patch

import pytest
import requests

from src.api_client import (
    _check_apilayer_error,
    _check_marketstack_error,
    _create_apilayer_headers,
    _create_marketstack_params,
    fetch_from_api,
    fetch_from_apilayer,
    fetch_from_marketstack,
    get_api_key,
)


# get_api_key


def test_get_api_key_success(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "123")
    assert get_api_key("TEST_KEY", "prov") == "123"


def test_get_api_key_missing(monkeypatch):
    monkeypatch.delenv("TEST_KEY", raising=False)
    with pytest.raises(RuntimeError):
        get_api_key("TEST_KEY", "prov")


# create headers / params

def test_create_apilayer_headers():
    assert _create_apilayer_headers("ABC") == {"apikey": "ABC"}


def test_create_marketstack_params():
    assert _create_marketstack_params("XYZ", {"a": 1}) == {
        "access_key": "XYZ",
        "a": 1,
    }


# Error checkers

@pytest.mark.parametrize(
    "data",
    [
        {"success": False, "error": {"info": "msg"}},
        {"success": False, "error": "text error"},
    ],
)
def test_check_apilayer_error_raises(data):
    with pytest.raises(RuntimeError):
        _check_apilayer_error(data)


def test_check_apilayer_error_ok():
    _check_apilayer_error({"success": True})  # should not raise


@pytest.mark.parametrize(
    "data",
    [
        {"error": {"message": "m1"}},
        {"error": "plain"},
    ],
)
def test_check_marketstack_error_raises(data):
    with pytest.raises(RuntimeError):
        _check_marketstack_error(data)


def test_check_marketstack_error_ok():
    _check_marketstack_error({"data": 1})  # should not raise


# fetch_from_api

def test_fetch_from_api_success(mock_response_success):
    with patch("requests.get", return_value=mock_response_success):
        result = fetch_from_api("http://test.com", {"q": 1})
        assert result == {"success": True, "data": 123}


def test_fetch_from_api_timeout():
    with patch("requests.get", side_effect=requests.Timeout):
        with pytest.raises(RuntimeError):
            fetch_from_api("http://x")


def test_fetch_from_api_connection_error():
    with patch("requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(RuntimeError):
            fetch_from_api("http://x")


def test_fetch_from_api_http_error():
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError(
        response=MagicMock(status_code=500)
    )
    with patch("requests.get", return_value=mock_resp):
        with pytest.raises(RuntimeError):
            fetch_from_api("http://x")


def test_fetch_from_api_invalid_json(mock_response_invalid_json):
    with patch("requests.get", return_value=mock_response_invalid_json):
        with pytest.raises(RuntimeError):
            fetch_from_api("http://x")


def test_fetch_from_api_calls_error_checker(mock_response_success):
    mock_checker = MagicMock()

    with patch("requests.get", return_value=mock_response_success):
        fetch_from_api("http://x", check_error_fn=mock_checker)

    mock_checker.assert_called_once()


# fetch_from_apilayer

@patch("src.api_client.fetch_from_api")
@patch("src.api_client._create_apilayer_headers")
@patch("src.api_client.get_api_key", return_value="KEY")
@patch("src.api_client.load_dotenv")
def test_fetch_from_apilayer(load_dotenv_mock, get_key_mock, headers_mock, fetch_api_mock):
    headers_mock.return_value = {"apikey": "KEY"}

    fetch_from_apilayer("live", {"a": 1})

    load_dotenv_mock.assert_called_once()
    get_key_mock.assert_called_once()
    headers_mock.assert_called_once_with("KEY")
    fetch_api_mock.assert_called_once()


# fetch_from_marketstack

@patch("src.api_client.fetch_from_api")
@patch("src.api_client._create_marketstack_params")
@patch("src.api_client.get_api_key", return_value="KEY")
@patch("src.api_client.load_dotenv")
def test_fetch_from_marketstack(load_dotenv_mock, get_key_mock, params_mock, fetch_api_mock):
    params_mock.return_value = {"access_key": "KEY", "a": 1}

    fetch_from_marketstack("tickers", {"a": 1})

    load_dotenv_mock.assert_called_once()
    get_key_mock.assert_called_once()
    params_mock.assert_called_once_with("KEY", {"a": 1})
    fetch_api_mock.assert_called_once()
