import sqlite3 as sql 
from socket import *
from threading import * #For multithreading. So mutltiple users can acces the server.
import json # For handling JSON data
from json import *
from requests import *

# Initializing database and creating tables
conn = sql.connect("accounts.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS accounts(username TEXT PRIMARY KEY, password TEXT, balance REAL)")
    
cursor.execute("CREATE TABLE IF NOT EXISTS portfolios(username TEXT, asset TEXT, quantity REAL, PRIMARY KEY (username, asset), FOREIGN KEY (username) REFERENCES accounts(username))")

cursor.execute("CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, asset_name TEXT, quantity REAL, action TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (username) REFERENCES accounts(username))")
conn.commit()
conn.close()


# Class to manage user accounts. Mainly to deal with Login and create account data
class Acc_Manager:
    
    # Simply verifies user input with the database
    def login(username,password):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username = ? AND password = ?", (username,password))
        conn.close()
    
    
    # For creating a new user
    def create_account(username,password,balance):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username =?", (username,))
        try:
            cursor.execute("INSERT INTO accounts (username,password,balance) VALUES (?, ?, ?)", (username,password,balance))
            conn.commit()
            return True # Return's True if the account creating was successful
        except sql.IntegrityError:
            return False #Return's False if user already exists in the DB.
        finally:
            conn.close()  


#The Accounts class handles account-level operations, including balance updates, transaction logging, and account data retrieval.
class Account:
    # Updates user balance in the database based on the action "deposit" or "withdraw"
    def update_balance_in_db(username, amount, action):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        try:
            if action == "deposit":
                cursor.execute("UPDATE accounts SET balance = balance + ? WHERE username = ?", (amount, username))
            
            elif action == "withdraw":
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE username = ? AND balance >= ?", (amount, username, amount))
            conn.commit()
            cursor.execute("SELECT balance FROM accounts WHERE username = ?", (username,))
            new_balance = cursor.fetchone()[0]
            Account.record_transactions_in_db(username, action, amount, action)
            return new_balance
        
        except sql.Error as e:
            print(f"Error processing balance: {e}")
            return None # Returns None incase of any Errors
        finally:
            conn.close()
    
    # Retrieves account information from the database to avoid loss of data when account has been created.
    def load_accounts_from_db(username):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, balance FROM accounts WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return {"username": row[0], "password": row[1] , "balance": row[2]} 
        conn.close()
        return None
    
    #Log's user transactions in the table 
    def record_transactions_in_db(username, asset, quantity, action):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (username, asset_name, quantity, action) VALUES (?, ?, ?, ?)", (username, asset, quantity, action))
        conn.commit()
    
    # Retrieves user transaction history (Limited to view a 50 transactions only)
    def view_transactions(username, limit=50):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT asset_name, quantity, action, date FROM transactions WHERE username = ? ORDER BY date DESC LIMIT ?", (username, limit))
            transactions = cursor.fetchall()
            if not transactions:  # Check if transactions list is empty
                return []
            return [list(item) for item in transactions]
        except sql.Error as e:
            print(f"Error retrieving transactions: {e}")
            return []
        finally:
            conn.close()

# Class handles the currencies and metals, including fetching live prices
class Asset:
    # Getting live prices from CoinGecko API as it is the best free alternative.
    def live_prices():
        url = "https://api.coingecko.com/api/v3/simple/price"
        # giving the parameters for the API to fetch specific data only
        param = {
            "ids": "bitcoin,ethereum,binancecoin,ripple,shiba-inu,pax-gold",
            "vs_currencies": "usd"
        }
        # Storing the asset prices in a dictionary 
        try:
            response = get(url, params=param)
            response.raise_for_status()
            data = response.json()
            live_asset_price = {
                "Bitcoin": data["bitcoin"]["usd"],
                "Ethereum": data["ethereum"]["usd"],
                "BNB": data["binancecoin"]["usd"],
                "XRP": data["ripple"]["usd"],
                "ShibaInu": data["shiba-inu"]["usd"],
                "Gold": data["pax-gold"]["usd"],
            }
            return live_asset_price
        except RequestException as e: # If too many calls are not accepted, it throws an error.
            print(f"Error Fetching live prices: {e}")
            return None
            
    # Using JSON to convert JSON string to into a Python Object.
    def get_asset_prices():
    
        live_prices = Asset.live_prices() 
        static_prices = {
        "Bitcoin": 79600.41,
        "Ethereum": 3193.53,
        "BNB": 637.67,
        "XRP": 0.586157,
        "Shiba": 0.586157,
        "Gold": 2684.64,
        "Silver": 31.3
        }    
        
        asset_prices = live_prices if live_prices else static_prices
        return dumps(asset_prices)
    

# Class handles portfolio related operations like adding and removing assets, viewing portfolio content 
class Portfolio:
    
    # Updates user portfolio based on the action "buy" or "sell"
    def update_portfolio_in_db(username, asset, quantity, action):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        
        try:
            if action == 'buy':
                cursor.execute("INSERT INTO portfolios (username, asset, quantity) VALUES (?, ?, ?) ON CONFLICT(username, asset) DO UPDATE SET quantity = quantity + ?", (username, asset, quantity, quantity))
                
            elif action == 'sell':
                cursor.execute("UPDATE portfolios SET quantity = quantity - ? WHERE username = ? AND asset = ? AND quantity >= ?", (quantity, username, asset, quantity))
                
            conn.commit()
            return cursor.rowcount > 0 
        except sql.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()   
    # Retrieves portfolio data 
    def view_portfolio(username):
        conn = sql.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT asset, quantity FROM portfolios WHERE username = ?", (username,))
        portfolio = cursor.fetchall()
        conn.close()
        return [list(item) for item in portfolio]

# Function to handle trades like buying or selling and updates account balance and user portfolio          
def process_trade(username, asset, quantity, action):
    assets = loads(Asset.get_asset_prices())
    asset_value = assets.get(asset)
    if not asset_value:
        return "Asset not found"
    
    total_cost = asset_value * quantity
    account = Account.load_accounts_from_db(username)
    
    if not account:
        return "User account not found"
    
    if action == 'buy':
        if account['balance'] < total_cost:
            return "Insufficient funds"
        new_balance = Account.update_balance_in_db(username, total_cost, "withdraw")
        if new_balance is not None:
            if Portfolio.update_portfolio_in_db(username ,asset, quantity, 'buy'):
                Account.record_transactions_in_db(username, asset, quantity, 'buy')
                return f"Asset {asset} Successfully bought ({quantity} unit(s)) | Total Value: {asset_value * quantity}"
            else:
                Account.update_balance_in_db(username, total_cost, "deposit") #Returning the funds back to the wallet if it fails.
        else:
            return "Failed to update balance"
        
    elif action == 'sell':
        if Portfolio.update_portfolio_in_db(username, asset, quantity, 'sell'):
            new_balance = Account.update_balance_in_db(username, total_cost, "deposit")
            if new_balance is not None:
                Account.record_transactions_in_db(username, asset, quantity, 'sell')
                return f"Asset {asset} Successfully sold ({quantity} unit(s)) | Total Value: {asset_value * quantity}"
            else:
                Portfolio.update_portfolio_in_db(username, asset, quantity, 'buy') # Returning the asset if the sell fails
        else:
            return f"Insufficient {asset} in portfolio"
    
    return f"Invalid action"    


# Main Function to handle Client-Server communications.
def handle_client(client_socket):
    #Handles requests from client(s), including login, Create Account, View Balance, etc.
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(f"Received: {data}")
            command = data.split(':')
            
            if command[0] == "login":
                username, password = command[1].split(',')
                username = username.strip()
                password = password.strip()
                account = Account.load_accounts_from_db(username)
                if account and account['password'] == password:
                    client_socket.send("True".encode())
                else:
                    client_socket.send("Flase".encode())
                    
            elif command[0] == "create_account":
                username , password, balance = command[1].split(',')
                username = username.strip()
                password = password.strip()
                balance = float(balance.strip())
                
                response = "True" if Acc_Manager.create_account(username, password, balance) else "False"
                client_socket.send(response.encode())
            
            elif command[0] == "balance":
                username = command[1].strip()
                account = Account.load_accounts_from_db(username)
                if account:
                    client_socket.send(f"Balance: {account['balance']:.2f}".encode())
                else:
                    client_socket.send("Error: User not found")
                    
            elif command[0] == "view_assets":
                asset_prices = Asset.get_asset_prices()
                try:
                    client_socket.send(asset_prices.encode())
                except Exception as e:
                    print (f"Asset prices can't be fetched right now....\n{e}")
                
            elif command[0] == "deposit":
                username, amount = command[1].split(',')
                try:
                    amount = float(amount)
                    new_balance = Account.update_balance_in_db(username, amount, "deposit")
                    if new_balance is not None:
                        client_socket.send(f"Amount ${amount:.2f} Sucessfully Deposited. New Balance: ${new_balance:.2f}".encode())
                    else:
                        client_socket.send("Error: Transaction failed".encode())    
                except (ValueError, SyntaxError, TypeError, Exception) as e:
                    client_socket.send(f"Error: {e}".encode())
                
            elif command[0] == "withdraw":
                username, amount = command[1].split(',')
                try:
                    amount = float(amount)
                    new_balance = Account.update_balance_in_db(username, amount, "withdraw")
                    if new_balance is not None:
                        client_socket.send(f"Amount ${amount:.2f} Successfully Withdrawn. New Balance: ${new_balance:.2f}".encode())
                    else:
                        client_socket.send("Error Insufficient funds".encode())
                except (ValueError, SyntaxError, TypeError, Exception) as e:
                    client_socket.send(f"Error: {e}".encode())
            
            elif command[0] in ["buy_asset", "sell_asset"]:
                username, asset, quantity = command[1].split(',')
                quantity = float(quantity)
                action = 'buy' if command[0] == "buy_asset" else 'sell'
                result = process_trade(username, asset, quantity, action)
                client_socket.send(result.encode())
                                    
            elif command[0] == "view_portfolio":
                try:
                    username = command[1].strip()
                    portfolio = Portfolio.view_portfolio(username)
                    client_socket.send(dumps(portfolio).encode())
                except Exception as e:
                    client_socket.send(f"Error: Something went wrong getting portfolio information...{str(e)}".encode()) 
            elif command[0] == "view_transaction":
                try:
                    username = command[1].strip()
                    transactions = Account.view_transactions(username)
                    if not transactions:
                        client_socket.send(dumps([]).encode('utf-8'))  # Send empty list
                    else:
                        client_socket.send(dumps(transactions).encode('utf-8'))
                except Exception as e:
                    client_socket.send(f"Error: Unable to retrieve transaction history. {str(e)}".encode())
    except Exception as e:
            print(f"Error: {e}")  # Log the error for debugging
    finally:
        client_socket.close()  # Ensure the socket is closed properly        

# Server starts and listens for a connection from the client side
def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('localhost', 5050))
    server_socket.listen(5)
    print("Server is running....")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        client_thread = Thread(target=handle_client, args=(client_socket,)) # For each client to be handled in a seperate thread.
        client_thread.start()

if __name__ == '__main__':
    main()  