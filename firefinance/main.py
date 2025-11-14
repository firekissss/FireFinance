from services import analyze_cashback_categories
from utils import print_banner
from views import main_page_view, services_page_view


def main():
    """
    main function, entry point for FireFinance
    """
    print_banner()
    print("\nHello! How are you?\n"
          "Here are pages that you can view from the menu:"
          "1. Main page\n"
          "2. Services (for now - only analyse cashback within given month and year)\n"
          "That's all for now. All results will appear as json string.\n")
    user_input = input("Enter the page number: ")
    if user_input == "1":
        date = input("Enter the date: ")
        print("OK lets go, look at this: \n")
        print(main_page_view(date if date else "2020-01-05 22:30:50"))

    if user_input == "2":
        month = input("Enter the month: ")
        year = input("Enter the year: ")
        print("OK lets go, look at this: \n")
        print(services_page_view(year if year else 2020, month if month else 1))


if __name__ == '__main__':
    main()
