import tkinter as tk
from socket import *
from tkinter import * 
from json import loads, JSONDecodeError

HOST = 'localhost'
PORT = 5050

# Function to send requests to the server and receive responses
def send_request(request):
    try:
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect((HOST,PORT))
            client_socket.send(request.encode())
            response = client_socket.recv(1024).decode()
            return response.strip()
    except ConnectionRefusedError:
        # Handles the case when the server is not running or unreachable
        return "Error Unable to connect to the servr at this time."
    except Exception as e:
        # Catches any other unexpected errors
        return f"An error occured: {e}"

# Function to handle user login
def login(username,password):
    response = send_request(f"login: {username},{password}")
    if response == "True":
        print(f"Welcome back {username}")
        user_menu(username)
        return True
    else:
        print("Account not found")
        return False

# Function to create a new user account
def create_account(username, password, balance):
    response = send_request(f"create_account:{username},{password},{float(balance)}")
    if response == "True":
        print(f"Account Created Successfully! Welcome {username}")
        return True
    else:
        print("Error: account already Exists")
        return False

# Function to display account balance
def display_account(username):
    response = send_request(f"balance:{username}")
    print(f"Account balance: {response}")

# Function to view available assets and their prices
def view_assets():
    response = send_request("view_assets")
    print(f"{'-'*28}\n Currently Available Assets \n{'-'*28}\n")
    try:
        # Parses the JSON response into a Python dictionary
        assets = loads(response) 
        if isinstance(assets, dict):
            for asset, price in assets.items():
                print(f"{asset}: ${price:.2f}\n")
        else:
            print("Error: Data provided is incorrectly formated...")
    except JSONDecodeError:
        # Handles the case when the server response is not valid JSON
        print("Error: Unable to parse asset data. Server response is not vaild JSON.")

# Function to add funds to the user's account
def add_funds(username,amount):
    while True:
        amount = float(input("Enter the amoun you would like to Deposit:\n>>> "))
        if amount > 0:
            response = send_request(f"deposit:{username},{amount}")
            print(response)
            return 
        else:
            print("Error: Invalid Input")
            return user_menu()

# Function to withdraw funds from the user's account
def withdraw_funds(username):
    try:
        while True:
            amount = float(input("Enter the amount you would like to Withdraw:\n>>> "))
            if amount > 0:
                response = send_request(f"withdraw:{username},{amount}")
                print(response)
                return 
            else:
                print("Error: Invalid Input")
    except (ValueError, TypeError) as e:
        # Handles invalid input types or conversion errors
        return f"Error: Something went wrong!\n{e}"

# Function to execute a trade (buy or sell assets)
def execute_trade(username, asset, quantity, action):
    response = send_request(f"{action}_asset:{username},{asset},{quantity}")
    print(response)

# Function to handle user input for trading
def trade_input(username, action):
    asset = input("Enter the asset name:\n>>> ")
    quantity = float(input("Enter the quantity:\n>>> "))
    execute_trade(username, asset, quantity, action)

# Function to view user's portfolio
def view_portfolio(username):
    response = send_request(f"view_portfolio:{username}")
    print(f"User: {username}'s Portfolio:\n{'-'*29}")
    try:
        portfolio = loads(response)
        if portfolio:
            for asset, quantity in portfolio:
                print(f"{asset}: {quantity:.2f} units")
        else:
            print("No assets found in portfolio.")
    except JSONDecodeError:
        # Handles the case when the server response is not valid JSON
        print("Error: Unable to parse portfolio data. Server response is not vaild JSON.")

# Function to view transaction history
def view_transaction_history(username):
    response = send_request(f"view_transaction:{username}")
    print(f"{'-'*38}\nUser: {username}'s Transaction History\n{'-'*38}\n Name | Quantity  |   Type    |        Date         |")
    try:
        transactions = loads(response) 
        if transactions:  # Check for non-empty transactions
            for asset_name, quantity, action, date in transactions:
                print(f"{asset_name} | {quantity:.2f} |  {action}  | {date} |")
        else:
            print("No transaction history available.")  # Handle empty transactions
    except JSONDecodeError:
        # Handles the case when the server response is not valid JSON
        print("Error: Unable to retrieve transaction history at the moment.")

# Function to display and handle the user menu
def user_menu(username):
    while True:
        print(f"{'-'*9}\nMain Menu\n{'-'*9}\n",
            "1. View Account Balance\n",
            "2. View Asset's\n",
            "3. Depsoit\n",
            "4. Withdraw\n",
            "5. Buy New Asset\n",
            "6. Sell Asset(s)\n",
            "7. View Portfolio Details\n",
            "8. View Transaction History\n",
            "9. Logout\n",
            "10. Exit")
        
        choice = input("Choose your desired operation (1-10)\n>>> ")
        
        if choice == '1':
            display_account(username)
        elif choice == '2':
            view_assets()
        elif choice == '3':
            add_funds(username,0)
        elif choice == '4':
            withdraw_funds(username)
        elif choice == '5':
            trade_input(username, 'buy')
        elif choice == '6':
            trade_input(username, 'sell')
        elif choice == '7':
            view_portfolio(username)
        elif choice == '8':
            view_transaction_history(username)
        elif choice == '9':
            print("Logging out and returning to the Main Menu...")
            return main()
        elif choice == '10':
            print("Exiting the program...Thank you for using BITWALLET")
            exit()
        else:
            print("ERROR: Invalid Input")

# Main function to start the program
def main():
    print("Welcome to BitWallet\n")
    while True:
        print("What would you like to do?\n1. Login\n2. Create Account\n3. Exit")
        choice = input("Your choice:\n>>> ")
        
        if choice == '1':
            username = input("Enter Username:\n>>> ")
            password = input("Enter Password:\n>>> ")
            if login(username, password):
                login(username, password)
            else:
                print("Login failed...Try again")
                return main()
        elif choice == '2':
            username = input("Enter Username:\n>>> ")
            password = input("Enter Password:\n>>> ")
            balance = input("Enter your Initial Balance:\n>>> ")
            create_account(username,password,balance)
            return main()
        elif choice == '3':
            print("Exiting the program...Thank you for using BITWALLET")
            break
        else:
            print("ERROR: Invalid Input")
            return main()

if __name__ == "__main__":
    main()
