import pandas as pd
import json

from src.utils import filter_data_by_date, _clean_cashback_data, calculate_cashback_by_category, _sort_results

from src.logs import get_logger

logger = get_logger(__name__)


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
    logger.info(f"Starting cashback analysis for {year}-{month:02d}, sort_by: '{sort_by}'")
    logger.debug(f"Input data shape: {data.shape}, columns: {list(data.columns)}")

    filtered_data = filter_data_by_date(data, year, month)
    logger.debug(f"After date filtering - shape: {filtered_data.shape}")

    if filtered_data.empty:
        logger.warning(f"No data found for period {year}-{month:02d}")
        return json.dumps({})

    cleaned_data = _clean_cashback_data(filtered_data)
    logger.debug(f"After cleaning - shape: {cleaned_data.shape}")

    if cleaned_data.empty:
        logger.warning("No valid cashback data after cleaning")
        return json.dumps({})

    cashback_results = calculate_cashback_by_category(cleaned_data)
    logger.debug(f"Cashback calculated for {len(cashback_results)} categories")

    if not cashback_results:
        logger.warning("No cashback results calculated")
        return json.dumps({})

    sorted_results = _sort_results(cashback_results, sort_by)
    logger.info(f"Cashback analysis completed successfully. Found {len(sorted_results)} categories")

    return json.dumps(sorted_results, ensure_ascii=False, indent=2)
