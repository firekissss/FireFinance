import pandas as pd
import json

from utils import filter_data_by_date, clean_cashback_data, calculate_cashback_by_category, sort_results


def analyze_cashback_categories(
        data: pd.DataFrame,
        year: int,
        month: int,
        sort_by: str = 'cat'
) -> str:
    """
    Main function for analyzing the profitability of enhanced cashback categories.

    Args:
        data (pd.DataFrame): Transaction data
        year (int): Year for analysis
        month (int): Month for analysis
        sort_by (str): Sorting parameter - 'cat' (alphabetically) or 'sum' (by amount)

    Returns:
        str: JSON with cashback analysis by categories
    """
    filtered_data = filter_data_by_date(data, year, month)
    if filtered_data.empty:
        return json.dumps({})
    cleaned_data = clean_cashback_data(filtered_data)
    if cleaned_data.empty:
        return json.dumps({})
    cashback_results = calculate_cashback_by_category(cleaned_data)
    sorted_results = sort_results(cashback_results, sort_by)

    return json.dumps(sorted_results, ensure_ascii=False, indent=2)
