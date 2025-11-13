import os

import requests
from dotenv import load_dotenv


def fetch_from_apilayer(endpoint: str, params: dict) -> dict:
    """
    Apilayer API access function.
    Handles errors and returns a JSON response.
    :param endpoint: endpoint of apilayer.com
    :param params: params for the request
    :return: response and data if successful, otherwise raises exception
    """
    load_dotenv()
    api_key = os.getenv("APILAYER_KEY")
    if not api_key:
        raise RuntimeError("API ключ не найден в .env (переменная APILAYER_KEY)")

    base_url = "https://api.apilayer.com/currency_data"
    url = f"{base_url}/{endpoint}"
    headers = {"apikey": api_key}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
    except requests.Timeout:
        raise RuntimeError("Превышено время ожидания ответа от API")
    except requests.ConnectionError:
        raise RuntimeError("Ошибка подключения к интернету или API недоступен")
    except requests.HTTPError as e:
        raise RuntimeError(f"Ошибка HTTP: {e.response.status_code}")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Некорректный JSON в ответе API")

    if not data.get("success", True):
        raise RuntimeError(f"API вернул ошибку: {data.get('error', 'Неизвестная ошибка')}")

    return data


def fetch_from_marketstack(endpoint: str, params: dict) -> dict:
    """
    Marketstack API access function.
    Handles errors and returns a JSON response.
    :param endpoint: endpoint of marketstack.com
    :param params: params for the request
    :return: response and data if successful, otherwise raises exception
    """
    load_dotenv()
    api_key = os.getenv("MARKETSTACK_KEY")
    if not api_key:
        raise RuntimeError("API ключ не найден в .env (переменная MARKETSTACK_KEY)")

    base_url = "http://api.marketstack.com/v2"
    url = f"{base_url}/{endpoint}"

    # ключ у marketstack называется access_key, а не apikey
    params = {"access_key": api_key, **params}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.Timeout:
        raise RuntimeError("Превышено время ожидания ответа от Marketstack API")
    except requests.ConnectionError:
        raise RuntimeError("Ошибка подключения к интернету или API недоступен")
    except requests.HTTPError as e:
        raise RuntimeError(f"Ошибка HTTP: {e.response.status_code}")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Некорректный JSON в ответе API")

    # у marketstack нет 'success', но может быть 'error'
    if "error" in data:
        err = data["error"]
        message = err.get("message", "Неизвестная ошибка")
        raise RuntimeError(f"Marketstack API вернул ошибку: {message}")

    return data