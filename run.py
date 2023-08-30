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
        answer = input("Do you need instructions? (y/n): ").lower()
        if answer == "y":
            print("The system is used for buying a selling clothes items. You will select if you are buying or selling (b/s) and then get further instructions")
            break
        elif answer == "n":
            print("Continuing to system start")
            break
        else:
            print("Invalid input, choose y/n")

instructions()