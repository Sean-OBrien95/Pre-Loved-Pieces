import gspread
from google.oauth2.service_account import Credentials

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
        answer = input("Do you need instructions? (y/n): \n").lower()
        if answer == "y":
            print("The system is used for buying a selling clothes items. You will select if you are buying or selling (b/s) and then get further instructions")
            break
        elif answer == "n":
            print("Continuing to system start")
            break
        else:
            print("Invalid input, choose y/n")
    

def buyer_or_seller():
    """
    Function to ask if user is buying or selling, and then return data to system
    """
    while True:
        b_or_s = input("Are you a buyer or a seller? (b/s): \n")
        if b_or_s == "b":
            print("Loading list of items...\n")
            break
        elif b_or_s == "s":
            print("Seller confirmed...\n")
            break
        else:
            print("Invalid input, choose b/s")

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

        for idx, row in enumerate(data, start=1):
            print(f"{idx}: {row}")
        
        if not data:
            print("No more available items")
            break
    
        try:
            selected_index = int(input("Enter the number of the item you would like to buy (or 0 to exit): "))

            if selected_index == 0:
                print("Exiting system...")
                break

            if 1 <= selected_index <= len(data):
                if data[selected_index - 1] not in selected_items:
                    selected_items.append(data[selected_index - 1])
                    print(f"{data[selected_index - 1]} selected")
                else: 
                    print("Item already selected.")
            else:
                print("Invalid input, try again.")
        
        except ValueError:
            print("Invalid input, try again.")
    
        continue_selection = input("Would you like to select another item? (y/n): ").lower()
        if continue_selection == "n":
            print("Continuing to list of items you selected")
            return selected_items
            break
        elif continue_selection != "y":
            print("invalid input, slected y/n")

    return selected_items

def purchase(selected_items_data):
    """
    Final function of buyer route, display back what the user selected, add the total, and 
    displays the total savings
    """

    total_price = 0

    print("Selected items: \n")
    for idx, item in enumerate(selected_items_data, start=1):
        print(f"{idx}: {item[0]} - Original Price: {item[1]} - Price: {item[3]}\n")
        total_price += float(item[3])

    total_original_price = sum(float(item[1]) for item in selected_items_data)
    total_discounted_price = sum(float(item[3]) for item in selected_items_data)
    total_savings = total_original_price - total_discounted_price

    print(f"Total price: {total_price}")
    print(f"Total savings: {total_savings}\n")

    while True:
        confirm_purchase = input("Are you happy with this purchase? (y/n): ").lower()
        if confirm_purchase == "y":
            print(f"Thank you for your purchase! You saved {total_savings}!")
            break
        elif confirm_purchase == "n":
            print("Removing items from cart...")
            break
        else:
            print("invalid input, please enter (y/n)")
        
    if confirm_purchase == "y":
        sheet = GSPREAD_CLIENT.open("pre_loved_pieces")
        items_sheet = sheet.worksheet("items")
        selected_rows = [idx + 2 for idx, _ in enumerate(selected_items_data)]
        for row_num in selected_rows:
            items_sheet.delete_rows(row_num)


instructions()
b_or_s = buyer_or_seller()
data = get_item_details()
selected_items_data = buyer_path(data)
purchase(selected_items_data)


