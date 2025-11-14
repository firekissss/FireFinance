from utils import print_banner
from views import main_page_view


def main():
    """
    main function, entry point for FireFinance
    """
    print_banner()
    print("\nHello! How are you?\n"
          "Here are pages that you can view from the menu:"
          "1. Main page\n"
          "That's all for now. All results will appear as json string.\n")
    user_input = input("Enter the page number: ")
    if user_input == "1":
        date = input("Enter the date: ")
        print("OK lets go, look at this: \n")
        print(main_page_view(date if date else "2020-01-05 22:30:50"))

if __name__ == '__main__':
    main()
