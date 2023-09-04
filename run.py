import gspread
from google.oauth2.service_account import Credentials
from colorama import Fore, Back, Style
from tabulate import tabulate

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("pre_loved_pieces")

def instructions():
    """
    Initial function to give explanation of how the program works to the user
    """
    print("Welcome to Pre-Loved Pieces, the second hand buy and sell system!\n")
    while True:
        answer = input(Style.RESET_ALL + "Do you need instructions? (y/n): \n").lower()
        if answer == "y":
            print("The system is used for buying a selling clothes items. You will select if you are buying or selling (b/s) and then get further instructions\n")
            break
        elif answer == "n":
            print("Continuing to system start\n")
            break
        else:
            print(Fore.RED + "Invalid input, choose y/n")
    

def buyer_or_seller():
    """
    Function to ask if user is buying or selling, and then return data to system
    """
    while True:
        b_or_s = input(Style.RESET_ALL + "Are you a buyer or a seller? (b/s): \n").lower()
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

def buyer_path(data):
    """
    Retrieves spreadsheet data and takes user to buyer options
    """

    selected_items = []

    while True:

        print("Items loaded. To select one, enter in the index number.")
        print("The items are displayed with a description, then original price, discount percent, and price after discount")

        headers = ["Index", "Description", "Original Price", "Discount Percent", "Price After Discount"]
        item_table = [[idx, *row] for idx, row in enumerate(data, start=1)]
        print(tabulate(item_table, headers=headers, tablefmt="fancy_grid"))
        
        if not data:
            print(Fore.RED + "No more available items")
            break
    
        try:
            selected_index = int(input(Style.RESET_ALL + "Enter the number of the item you would like to buy (or 0 to exit): \n"))

            if selected_index == 0:
                return []

            if 1 <= selected_index <= len(data):
                if data[selected_index - 1] not in selected_items:
                    selected_items.append(data[selected_index - 1] + [selected_index + 1])
                    print(f"{data[selected_index - 1]} selected\n")
                else: 
                    print(Fore.RED + "Item already selected.\n")
    
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
    
            continue_selection = input(Style.RESET_ALL + "Would you like to select another item? (y/n): \n").lower()
            if continue_selection == "n":
                print("Continuing to list of items you selected")
                return selected_items
                break
            elif continue_selection == "y":
                break
            else:
                print(Fore.RED + "Invalid input, please enter y/n")
                continue

    return selected_items

def purchase(selected_items_data):
    """
    Final function of buyer route, display back what the user selected, add the total, and 
    displays the total savings. Remove selected items from google sheet
    """

    total_price = 0
    rows_to_delete = []

    print("Selected items: \n")
    for idx, item in enumerate(selected_items_data, start=1):
        print(f"{idx}: {item[0]} - Original Price: €{item[1]} - Price: €{item[3]}\n")
        total_price += int(item[3])
        rows_to_delete.append(int(item[4]))

    total_original_price = sum(int(item[1]) for item in selected_items_data)
    total_discounted_price = sum(int(item[3]) for item in selected_items_data)
    total_savings = total_original_price - total_discounted_price

    print(f"Total price: €{total_price}")
    print(Fore.GREEN + f"Total savings: €{total_savings}\n")

    while True:
        confirm_purchase = input(Style.RESET_ALL + "Are you happy with this purchase? (y/n): \n").lower()
        if confirm_purchase == "y":
            print(Fore.GREEN + f"Thank you for your purchase! You saved €{total_savings}!")
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
            items_sheet.delete_rows(row_num)

def seller_path():
    """
    Takes user to seller options
    """
    while True: 
        item_name = input(Style.RESET_ALL + "Enter the item you would like to sell (eg top, hat, etc): \n")
        if item_name.isalpha():
            break
        else:
            print(Fore.RED + "Invalid input, please only use letters")

    while True:
        try:
            original_value = int(input(Style.RESET_ALL + "Enter the original value of this item: \n"))
            break
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a whole number.")

    while True: 
        discount_percent = input(Style.RESET_ALL + "Enter what percent you would like to discount (1-99): \n")
        if discount_percent.isdigit():
            discount_percent = int(discount_percent)
            if 1 <= discount_percent <= 99:
                break
            else:
                print(Fore.RED + "Invalid input, percent must be between 1 - 99")
        else:
            print(Fore.RED + "Invalid input, try again...")

    discounted_value = round(original_value - (original_value * discount_percent / 100))

    print(f"\nItem: {item_name}")
    print(f"Original Value: €{original_value}")
    print(f"Discount Percent: {discount_percent}%")
    print(f"Discount Value: €{discounted_value}")

    return item_name, original_value, discount_percent, discounted_value

def confirm_sale(item_name, original_value, discount_percent, discounted_value):
    """
    Final stage of seller path. Updates spreadsheet with the user input
    """
    while True: 
        confirm = input(Style.RESET_ALL + "Are you happy with this sale? (y/n): \n")
        if confirm == "y":
            sheet = GSPREAD_CLIENT.open("pre_loved_pieces")
            items_sheet = sheet.worksheet("items")

            item_details = [item_name, original_value, discount_percent, discounted_value]
            items_sheet.append_rows([item_details])

            print(Fore.GREEN + f"Sale successful, you just made €{discounted_value}!")
            return True

        elif confirm == "n":
            print(Fore.RED + "Sale cancelled, exiting system...")
            return False

        else: 
            print(Fore.RED + "Invalid input, please enter (y/n)")

def start():
    instructions()
    b_or_s = buyer_or_seller()
    if b_or_s == "b":
        data = get_item_details()
        selected_items_data = buyer_path(data)
        if selected_items_data == []:
            print(Fore.RED + "\nExiting system")
        else:
            purchase(selected_items_data)
    else:
        item_name, original_value, discount_percent, discounted_price = seller_path()
        sale_confirmed = confirm_sale(item_name, original_value, discount_percent, discounted_price)
        if sale_confirmed:
            pass
        else: 
            print(Fore.RED + "Clearing item data")

if __name__ == "__main__":
    start()
