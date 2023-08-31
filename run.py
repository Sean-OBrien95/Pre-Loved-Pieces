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
            print("Loading list of items...")
            break
        elif b_or_s == "s":
            print("Seller confirmed...")
            break
        else:
            print("Invalid input, choose b/s")

    return b_or_s
    
instructions()
b_or_s = buyer_or_seller()
print(b_or_s)

