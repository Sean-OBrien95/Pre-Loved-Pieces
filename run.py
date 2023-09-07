import gspread
from google.oauth2.service_account import Credentials
from colorama import Fore, Back, Style, init
from tabulate import tabulate
init(autoreset=True)

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("pre_loved_pieces")


class UserName:
    """
    Class to take users name and display it back.
    Used after successful sale/purchase
    """
    def __init__(self):
        self.name = None

    def get_name(self):
        while True:
            self.name = input("Please enter your name: \n")
            if self.name.isalpha() and len(self.name) <= 10:
                print(f"Welcome {self.name}!")
                break
            else:
                print(Fore.RED + "Incorrect input, must have < 10 letters")


def instructions():
    """
    Initial function to give explanation of how the program works to the user
    """
    print("Welcome to Pre-Loved Pieces!")
    print("The second hand buy and sell system!\n")
    while True:
        answer = input("Do you need instructions? (y/n): \n").lower()
        if answer == "y":
            print("The system is used for buying a selling clothes items.")
            print("You will select if you are buying or selling (b/s)")
            print("and then get further instructions\n")
            break
        elif answer == "n":
            print("Continuing to system start\n")
            break
        else:
            print(Fore.RED + "Invalid input, choose y/n")


def buyer_or_seller():
    """
    Function to ask if user is buying or selling, and then
    return data to system
    """
    while True:
        b_or_s = input("Are you a buyer or a seller? (b/s): \n").lower()
        if b_or_s == "b":
            print("Loading list of items...\n")
            break
        elif b_or_s == "s":
            print("Seller confirmed...\n")
            break
        else:
            print(Fore.RED + "Invalid input, choose b/s")

    return b_or_s


def get_item_details():
    """
    Get the item details from the googlesheet, ignoring the top row
    """
    sheet = GSPREAD_CLIENT.open("pre_loved_pieces")
    items_sheet = sheet.worksheet("items")

    data = items_sheet.get_all_values()[1:]

    return data


def buyer_path(data, rows_to_delete):
    """
    Retrieves spreadsheet data and takes user to buyer options
    """

    selected_items = []

    while True:

        print("Items loaded. To select one, enter in the index number.")
        print("The items are displayed with a description, then")
        print("original price, discount percent, and price after discount")

        # Creates a table with indexing

        headers = ["Index", "Item", "Price",
                   "Percent", "Discount Price"]
        item_table = [[idx, *row] for idx, row in enumerate(data, start=1)]
        print(tabulate(item_table, headers=headers, tablefmt="fancy_grid"))

        if not data:
            print(Fore.RED + "No more available items")
            break

        try:
            print("Please enter the number of")
            selected_index = int(input("the item you would like to buy: \n"))

            # Handles selected item and flags if item already selected

            if 1 <= selected_index <= len(data):
                if data[selected_index - 1] not in [item[0:4]
                   for item in selected_items]:
                    selected_items.append(data[selected_index - 1]
                                          + [selected_index])
                    print(f"{data[selected_index - 1]} selected\n")
                else:
                    print(Fore.RED + "Item already selected.\n")

                rows_to_delete.append(selected_index)

            else:
                print(Fore.RED + "Invalid input, try again.\n")
                continue

        except ValueError:
            print(Fore.RED + "Invalid input, try again.\n")
            continue

        if len(selected_items) == len(data):
            print("You have selected all the items")
            return selected_items

        while True:

            continue_selection = input("Select another item?(y/n): \n").lower()
            if continue_selection == "n":
                print("Continuing to list of items you selected")
                return selected_items
            elif continue_selection == "y":
                break
            else:
                print(Fore.RED + "Invalid input, please enter y/n")
                continue

    return selected_items


def purchase(selected_items_data, rows_to_delete, user_name):
    """
    Final function of buyer route, display back what the user selected,
    add the total, and displays the total savings. Remove selected
    items from google sheet
    """

    total_price = 0
    rows_to_delete = []

    print("Selected items: \n")
    for idx, item in enumerate(selected_items_data, start=1):
        print(f"{idx}:{item[0]} Original Price:€{item[1]} Price:€{item[3]}\n")
        total_price += int(item[3])
        rows_to_delete.append(int(item[4]))

    # shows back price and discount value

    total_original_price = sum(int(item[1]) for item in selected_items_data)
    total_discounted_price = sum(int(item[3]) for item in selected_items_data)
    total_savings = total_original_price - total_discounted_price

    print(f"Total price: €{total_price}")
    print(Fore.GREEN + f"Total savings: €{total_savings}\n")

    while True:
        confirm_purchase = input("Happy with this purchase? (y/n): \n").lower()
        if confirm_purchase == "y":
            print(Fore.GREEN + "Thank you for your purchase!")
            print(f"You saved €{total_savings} {user_name}!")
            break
        elif confirm_purchase == "n":
            print(Fore.RED + "Removing items from cart...")
            break
        else:
            print(Fore.RED + "invalid input, please enter (y/n)")

    if confirm_purchase == "y":
        sheet = GSPREAD_CLIENT.open("pre_loved_pieces")
        items_sheet = sheet.worksheet("items")

        rows_to_delete.sort(reverse=True)
        for row_num in rows_to_delete:
            items_sheet.delete_rows(row_num + 1)


def seller_path():
    """
    Takes user to seller options
    """
    while True:
        print("Enter the item you would like to sell")
        item_name = input("Such as Hat, Top, Skirt, etc: \n")
        if item_name.isalpha() and len(item_name) <= 10:
            break
        else:
            print(Fore.RED + "Invalid input, please only use letters ( < 10)")

    while True:
        try:
            original_value = int(input(
                                 "Enter the original value of this item: \n"))
            if 1 <= original_value <= 999:
                break
            else:
                print(Fore.RED +
                      "Invalid input. Please enter a number between 1-999.")
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a whole number.")

    while True:
        discount_percent = input("Enter the discount percent: \n")
        if discount_percent.isdigit() and len(discount_percent) <= 3:
            discount_percent = int(discount_percent)
            if 1 <= discount_percent <= 99:
                break
            else:
                print(Fore.RED + "Invalid input, percent must be between 1-99")
        else:
            print(Fore.RED + "Invalid input, try again...")

    discounted_value = round(int(original_value
                             - (original_value * discount_percent / 100)))

    print(f"\nItem: {item_name}")
    print(f"Original Value: €{original_value}")
    print(f"Discount Percent: {discount_percent}%")
    print(f"Discount Value: €{discounted_value}")

    return item_name, original_value, discount_percent, discounted_value


def confirm_sale(item_name, original_value,
                 discount_percent, discounted_value, user_name):
    """
    Final stage of seller path. Updates spreadsheet with the user input
    """
    while True:
        confirm = input("Are you happy with this sale? (y/n): \n")
        if confirm == "y":
            sheet = GSPREAD_CLIENT.open("pre_loved_pieces")
            items_sheet = sheet.worksheet("items")

            # Add inputted data to spreadsheet

            item_details = [item_name, original_value,
                            discount_percent, discounted_value]
            items_sheet.append_rows([item_details])

            print(Fore.GREEN + "Sale successful!")
            print(Fore.GREEN +
                  f"You just made €{discounted_value} {user_name}!")
            return True

        elif confirm == "n":
            print(Fore.RED + "Sale cancelled, exiting system...")
            return False

        else:
            print(Fore.RED + "Invalid input, please enter (y/n)")


def start():
    user_input = UserName()
    user_input.get_name()
    instructions()
    while True:
        b_or_s = buyer_or_seller()
        rows_to_delete = []
        if b_or_s == "b":
            data = get_item_details()
            selected_items_data = buyer_path(data, rows_to_delete)
            purchase(selected_items_data, rows_to_delete, user_input.name)
        else:
            item_name, original_value, discount_percent, discounted_value = seller_path()  # noqa
            sale_confirmed = confirm_sale(item_name, original_value,
                                          discount_percent, discounted_value,
                                          user_input.name)
            if sale_confirmed:
                pass
            else:
                print(Fore.RED + "Clearing item data")

        another_item = input(Style.RESET_ALL +
                             "Buy/sell another item? (y/n): \n").lower()
        if another_item == "n":
            print(Fore.RED + "Exiting systems")
            break


if __name__ == "__main__":
    start()
