import logging

from src.logs import get_logger, setup_logging
from src.utils import print_banner
from src.views import main_page_view, reports_page_view, services_page_view


logger = get_logger(__name__)


def main() -> None:
    """
    main function, entry point for FireFinance
    """
    setup_logging(
        level=logging.DEBUG,
        enable_console=True,
        enable_file=True
    )

    logger.info("FireFinance application started")

    try:
        print_banner()
        logger.debug("Banner displayed")

        print("\nHello! How are you?\n"
              "Here are pages that you can view from the menu:\n"
              "1. Main page\n"
              "2. Services (for now - only analyse cashback within given month and year)\n"
              "3. Reports (for now - only spending by categories)\n"
              "That's all for now. All results will appear as json string.\n")

        user_input = input("Enter the page number: ")
        logger.info(f"User selected page: {user_input}")

        if user_input == "1":
            date = input("Enter the date: ")
            logger.debug(f"Main page requested with date: {date}")
            print("OK lets go, look at this: \n")
            result = main_page_view(date if date else "2020-01-30 22:30:50")
            print(result)
            logger.info("Main page view completed successfully")

        elif user_input == "2":
            month = input("Enter the month: ")
            year = input("Enter the year: ")
            logger.debug(f"Services page requested with year: {year}, month: {month}")
            print("OK lets go, look at this: \n")
            result = services_page_view(
                int(year) if year else 2020,
                int(month) if month else 1
            )
            print(result)
            logger.info("Services page view completed successfully")

        elif user_input == "3":
            date = input("Enter the date: ")
            cat_name = input("Enter the category name: ")
            out_file = input("Enter the output report file (empty for default): ").strip()
            logger.debug(f"Reports page requested with category: {cat_name}, date: {date}, output_file: {out_file}")

            print("\nOK lets go, look at this:\n")

            result = reports_page_view(
                cat_name,
                date if date else None,
                output_file=out_file if out_file else None
            )

            if input("1 if u wanna see the file content: ") == "1":
                print(result)
            else:
                print("done, go check the file")
            logger.info("Reports page view completed successfully")

        else:
            logger.warning(f"Invalid page number entered: {user_input}")
            print("Invalid page number!")

        logger.info("FireFinance application finished successfully")

    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == '__main__':
    main()
