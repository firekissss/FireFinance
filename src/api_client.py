import os
from typing import Optional, Callable, Any

import requests
from dotenv import load_dotenv


def get_api_key(env_var: str, provider_name: str) -> str:
    """
    Retrieves API key from environment variables.

    Args:
        env_var: Environment variable name
        provider_name: API provider name for error messages

    Returns:
        str: API key

    Raises:
        RuntimeError: If API key is not found
    """
    api_key = os.getenv(env_var)
    if not api_key:
        raise RuntimeError(f"API ключ не найден в .env ({env_var}) для {provider_name}")
    return api_key


def create_apilayer_headers(api_key: str) -> dict:
    """
    Creates headers for Apilayer API.

    Args:
        api_key: API key

    Returns:
        dict: Headers dictionary
    """
    return {"apikey": api_key}


def create_marketstack_params(api_key: str, additional_params: dict) -> dict:
    """
    Creates parameters for Marketstack API.

    Args:
        api_key: API key
        additional_params: Additional parameters for the request

    Returns:
        dict: Combined parameters dictionary
    """
    return {"access_key": api_key, **additional_params}


def check_apilayer_error(data: dict) -> None:
    """
    Checks for errors in Apilayer API response.

    Args:
        data: Response data

    Raises:
        RuntimeError: If API response indicates an error
    """
    if not data.get("success", True):
        error_info = data.get('error', {})
        error_message = error_info.get('info', 'Неизвестная ошибка') if isinstance(error_info, dict) else str(
            error_info)
        raise RuntimeError(f"Apilayer ошибка: {error_message}")


def check_marketstack_error(data: dict) -> None:
    """
    Checks for errors in Marketstack API response.

    Args:
        data: Response data

    Raises:
        RuntimeError: If API response indicates an error
    """
    if "error" in data:
        error_data = data["error"]
        error_message = error_data.get('message', 'Неизвестная ошибка') if isinstance(error_data, dict) else str(
            error_data)
        raise RuntimeError(f"Marketstack ошибка: {error_message}")


def fetch_from_api(
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        check_error_fn: Optional[Callable[[dict], Any]] = None
) -> dict:
    """
    Universal function for API requests.
    Executes request, handles common errors, parses JSON.

    Args:
        url: Full request URL
        params: GET parameters
        headers: HTTP headers
        check_error_fn: Function for checking API response errors

    Returns:
        dict: Parsed JSON response

    Raises:
        RuntimeError: For various API-related errors
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
    """
    Fetches data from Apilayer API.

    Args:
        endpoint: API endpoint
        params: Request parameters

    Returns:
        dict: API response data
    """
    load_dotenv()

    api_key = get_api_key("APILAYER_KEY", "Apilayer")
    base_url = "https://api.apilayer.com/currency_data"
    url = f"{base_url}/{endpoint}"
    headers = create_apilayer_headers(api_key)

    return fetch_from_api(
        url=url,
        params=params,
        headers=headers,
        check_error_fn=check_apilayer_error
    )


def fetch_from_marketstack(endpoint: str, params: dict) -> dict:
    """
    Fetches data from Marketstack API.

    Args:
        endpoint: API endpoint
        params: Request parameters

    Returns:
        dict: API response data
    """
    load_dotenv()

    api_key = get_api_key("MARKETSTACK_KEY", "Marketstack")
    base_url = "http://api.marketstack.com/v2"
    url = f"{base_url}/{endpoint}"
    request_params = create_marketstack_params(api_key, params)

    return fetch_from_api(
        url=url,
        params=request_params,
        headers=None,
        check_error_fn=check_marketstack_error
    )