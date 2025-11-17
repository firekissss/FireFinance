import functools
import json
import logging
import os
from datetime import datetime
from typing import Any, Callable, TypeVar, overload

import pandas as pd


# path to reports default directory
DEFAULT_REPORT_DIR = "../data/reports"

F = TypeVar("F", bound=Callable[..., Any])


@overload
def report_to_file(filename: F) -> F:
    pass


@overload
def report_to_file(filename: str | None) -> Callable[[F], F]:
    pass


def report_to_file(filename: Any = None) -> Any:
    """
    Decorator: saves the function result (DataFrame or dict)
    to a JSON file.
    If filename is not provided — a default file is created.

    Args:
        filename: Output filename. If None, generates default filename.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Default filename generation
            out_file = filename
            if out_file is None:
                fname = f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                out_file = os.path.join(DEFAULT_REPORT_DIR, fname)
            else:
                # если пользователь ввёл только имя — кладём его в папку reports
                if not os.path.isabs(out_file):
                    out_file = os.path.join(DEFAULT_REPORT_DIR, out_file)

            os.makedirs(os.path.dirname(out_file), exist_ok=True)

            # Convert DataFrame to JSON-friendly format
            if isinstance(result, pd.DataFrame):
                # pandas сам умеет сериализовать Timestamp
                result.to_json(out_file, orient="records", indent=4, force_ascii=False, date_format="iso")
            else:
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)

            print(f"Отчёт сохранён в файл: {out_file}")
            return result

        return wrapper  # type: ignore

    # Handle decorator without parameters: @report_to_file
    if callable(filename):
        func = filename
        filename = None
        return decorator(func)

    return decorator


# log


def log_exceptions(logger: logging.Logger) -> Callable:
    """
    Decorator that automatically logs any unhandled exceptions raised within the wrapped function.

    When an exception occurs, it is logged with ERROR level (including the full stack trace)
    using the provided logger, and then re-raised to preserve the original behavior.

    Parameters
    ----------
    logger : logging.Logger
        The logger instance used to record error messages.

    Returns
    -------
    Callable
        A decorator that wraps the target function with automatic exception logging.

    Raises
    ------
    Exception
        Any exception raised inside the wrapped function is logged and re-raised.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(str(e))
                raise

        return wrapper

    return decorator
