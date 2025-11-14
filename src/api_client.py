import os

import requests
from dotenv import load_dotenv


def fetch_from_api(
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        check_error_fn=None
) -> dict:
    """
    Универсальная функция для запросов к API.
    Выполняет запрос, обрабатывает типовые ошибки, парсит JSON.

    :param url: полный URL запроса
    :param params: GET параметры
    :param headers: HTTP заголовки
    :param check_error_fn: функция проверки ошибки ответа API
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
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

    if check_error_fn:
        check_error_fn(data)

    return data


def fetch_from_apilayer(endpoint: str, params: dict) -> dict:
    load_dotenv()
    api_key = os.getenv("APILAYER_KEY")
    if not api_key:
        raise RuntimeError("API ключ не найден в .env (APILAYER_KEY)")

    base_url = "https://api.apilayer.com/currency_data"
    url = f"{base_url}/{endpoint}"

    headers = {"apikey": api_key}

    def check_error(data):
        if not data.get("success", True):
            raise RuntimeError(f"Apilayer ошибка: {data.get('error', 'Неизвестная ошибка')}")

    return fetch_from_api(
        url=url,
        params=params,
        headers=headers,
        check_error_fn=check_error
    )


def fetch_from_marketstack(endpoint: str, params: dict) -> dict:
    load_dotenv()
    api_key = os.getenv("MARKETSTACK_KEY")
    if not api_key:
        raise RuntimeError("API ключ не найден в .env (MARKETSTACK_KEY)")

    base_url = "http://api.marketstack.com/v2"
    url = f"{base_url}/{endpoint}"

    # Marketstack всегда требует access_key
    params = {"access_key": api_key, **params}

    def check_error(data):
        if "error" in data:
            raise RuntimeError(f"Marketstack ошибка: {data['error'].get('message', 'Неизвестная ошибка')}")

    return fetch_from_api(
        url=url,
        params=params,
        headers=None,
        check_error_fn=check_error
    )
