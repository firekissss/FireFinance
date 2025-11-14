import functools
import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd

# path to reports default directory
DEFAULT_REPORT_DIR = "../data/reports"


def report_to_file(filename: Optional[str] = None):
    """
    Decorator: saves the function result (DataFrame or dict)
    to a JSON file.
    If filename is not provided — a default file is created.

    Args:
        filename: Output filename. If None, generates default filename.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
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

            # Convert DataFrame to JSON-friendly format
            if isinstance(result, pd.DataFrame):
                # pandas сам умеет сериализовать Timestamp
                result.to_json(out_file, orient="records", indent=4, force_ascii=False, date_format='iso')
            else:
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)

            print(f"Отчёт сохранён в файл: {out_file}")
            return result

        return wrapper

    # Handle decorator without parameters: @report_to_file
    if callable(filename):
        func = filename
        filename = None
        return decorator(func)

    return decorator
