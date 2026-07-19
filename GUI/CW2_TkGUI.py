import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from socket import socket, AF_INET, SOCK_STREAM
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

HOST = 'localhost'
PORT = 5050

# Function to send a request to the server
def send_request(request):
    try:
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.send(request.encode())
            response = client_socket.recv(1024).decode()
            return response.strip()
    except ConnectionRefusedError:
        return "Error: Unable to connect to the server."
    except Exception as e:
        return f"Error: {e}"

# Function to login
def login(username, password):
    response = send_request(f"login:{username},{password}")
    return response == "True"

# Function to create an account
def create_account(username, password, balance):
    try:
        balance = float(balance)
        response = send_request(f"create_account:{username},{password},{balance}")
        return response == "True"
    except ValueError:
        return False

# Function to display account balance
def get_balance(username):
    return send_request(f"balance:{username}")

# Function to view available assets
def get_assets():
    response = send_request("view_assets")
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {}

# Function to refresh portfolio data
def get_portfolio(username):
    response = send_request(f"view_portfolio:{username}")
    try:
        
        return json.loads(str(response))
    except json.JSONDecodeError:
        return  json.loads(' ')

# Function to get transaction history
def get_transactions(username):
    response = send_request(f"view_transaction:{username}")
    try:
        return json.loads(str(response))
    except json.JSONDecodeError:
        return  []

# Tkinter Login Window
def login_window():
    root = tk.Tk()
    root.title("Crypto Wallet - Login")

    tk.Label(root, text="Username:").grid(row=0, column=0, pady=5)
    username_entry = tk.Entry(root)
    username_entry.grid(row=0, column=1, pady=5)

    tk.Label(root, text="Password:").grid(row=1, column=0, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, pady=5)

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()
        if login(username, password):
            root.destroy()
            main_dashboard(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def handle_create_account():
        create_window = tk.Toplevel(root)
        create_window.title("Create Account")

        tk.Label(create_window, text="Username:").grid(row=0, column=0, pady=5)
        new_username_entry = tk.Entry(create_window)
        new_username_entry.grid(row=0, column=1, pady=5)

        tk.Label(create_window, text="Password:").grid(row=1, column=0, pady=5)
        new_password_entry = tk.Entry(create_window, show="*")
        new_password_entry.grid(row=1, column=1, pady=5)

        tk.Label(create_window, text="Initial Balance:").grid(row=2, column=0, pady=5)
        initial_balance_entry = tk.Entry(create_window)
        initial_balance_entry.grid(row=2, column=1, pady=5)

        def submit_create_account():
            username = new_username_entry.get()
            password = new_password_entry.get()
            balance = initial_balance_entry.get()
            if create_account(username, password, balance):
                messagebox.showinfo("Success", "Account created successfully!")
                create_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to create account. Ensure all fields are valid.")

        tk.Button(create_window, text="Submit", command=submit_create_account).grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(root, text="Login", command=handle_login).grid(row=2, column=0, columnspan=2, pady=10)
    tk.Button(root, text="Create Account", command=handle_create_account).grid(row=3, column=0, columnspan=2)

    root.mainloop()

# Main Dashboard
def main_dashboard(username):
    dashboard = tk.Tk()
    dashboard.title("Crypto Wallet - Dashboard")

    # Graph Section
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_title("Portfolio Profit & Loss")
    ax.set_ylabel("Value ($)")
    ax.set_xlabel("Assets")
    canvas = FigureCanvasTkAgg(fig, master=dashboard)
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def refresh_portfolio():
        portfolio = get_portfolio(username)
        if portfolio:
            assets, values = zip(*portfolio)
            ax.clear()
            ax.bar(assets, values, color="blue")
            ax.set_title("Portfolio Profit & Loss")
            ax.set_ylabel("Value ($)")
            ax.set_xlabel("Assets")
            canvas.draw()
        else:
            messagebox.showinfo("Portfolio", "No portfolio data available.")

    # Account Balance
    balance_label = tk.Label(dashboard, text=f"Account Balance: Loading...")
    balance_label.pack(pady=10)

    def refresh_balance():
        balance = get_balance(username)
        balance_label.config(text=f"Account Balance: {balance}")

    tk.Button(dashboard, text="Refresh Account Balance", command=refresh_balance).pack(pady=5)

    # View Assets Button
    def view_assets_window():
        assets_window = tk.Toplevel(dashboard)
        assets_window.title("Available Assets")
        assets = get_assets()

        if assets:
            for asset, price in assets.items():
                tk.Label(assets_window, text=f"{asset}: ${price:.2f}").pack(pady=2)
        else:
            tk.Label(assets_window, text="No assets available.").pack(pady=10)

    tk.Button(dashboard, text="View Assets", command=view_assets_window).pack(pady=5)

    # Buy Asset
    def buy_asset_window():
        buy_window = tk.Toplevel(dashboard)
        buy_window.title("Buy Asset")

        tk.Label(buy_window, text="Select Asset:").grid(row=0, column=0, pady=5)
        asset_dropdown = ttk.Combobox(buy_window, values=list(get_assets().keys()))
        asset_dropdown.grid(row=0, column=1, pady=5)

        tk.Label(buy_window, text="Quantity:").grid(row=1, column=0, pady=5)
        quantity_entry = tk.Entry(buy_window)
        quantity_entry.grid(row=1, column=1, pady=5)

        def submit_buy():
            asset = asset_dropdown.get()
            try:
                quantity = float(quantity_entry.get())
                response = send_request(f"buy_asset:{username},{asset},{quantity}")
                messagebox.showinfo("Buy Asset", response)
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity.")

        tk.Button(buy_window, text="Buy", command=submit_buy).grid(row=2, column=0, columnspan=2, pady=10)

    tk.Button(dashboard, text="Buy Asset", command=buy_asset_window).pack(pady=5)

    # Sell Asset
    def sell_asset_window():
        sell_window = tk.Toplevel(dashboard)
        sell_window.title("Sell Asset")

        tk.Label(sell_window, text="Select Asset:").grid(row=0, column=0, pady=5)
        asset_dropdown = ttk.Combobox(sell_window, values=list(get_assets().keys()))
        asset_dropdown.grid(row=0, column=1, pady=5)

        tk.Label(sell_window, text="Quantity:").grid(row=1, column=0, pady=5)
        quantity_entry = tk.Entry(sell_window)
        quantity_entry.grid(row=1, column=1, pady=5)

        def submit_sell():
            asset = asset_dropdown.get()
            try:
                quantity = float(quantity_entry.get())
                response = send_request(f"sell_asset:{username},{asset},{quantity}")
                messagebox.showinfo("Sell Asset", response)
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity.")

        tk.Button(sell_window, text="Sell", command=submit_sell).grid(row=2, column=0, columnspan=2, pady=10)

    tk.Button(dashboard, text="Sell Asset", command=sell_asset_window).pack(pady=5)

    # View Account Details
    def account_details_window():
        account_window = tk.Toplevel(dashboard)
        account_window.title("Account Details")

        def view_portfolio():
            portfolio = get_portfolio(username)
            if portfolio:
                portfolio_window = tk.Toplevel(account_window)
                portfolio_window.title("Portfolio")
                for asset, quantity in portfolio:
                    tk.Label(portfolio_window, text=f"{asset}: {quantity} units").pack(pady=2)
            else:
                messagebox.showinfo("Portfolio", "No assets in portfolio.")

        def deposit():
            amount = simpledialog.askfloat("Deposit", "Enter amount to deposit:")
            if amount and amount > 0:
                response = send_request(f"deposit:{username},{amount}")
                messagebox.showinfo("Deposit", response)

        def withdraw():
            amount = simpledialog.askfloat("Withdraw", "Enter amount to withdraw:")
            if amount and amount > 0:
                response = send_request(f"withdraw:{username},{amount}")
                messagebox.showinfo("Withdraw", response)

        def view_transaction_history():
            transactions = get_transactions(username)
            if transactions:
                history_window = tk.Toplevel(account_window)
                history_window.title("Transaction History")
                scroll_frame = tk.Frame(history_window)
                scroll_frame.pack(fill=tk.BOTH, expand=True)

                canvas = tk.Canvas(scroll_frame)
                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                scrollbar = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                frame = tk.Frame(canvas)
                canvas.create_window((0, 0), window=frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                for asset_name, quantity, action, date in transactions:
                    tk.Label(frame, text=f"{asset_name}: {quantity} | {action} | {date}").pack(pady=2)

                frame.update_idletasks()
                canvas.config(scrollregion=canvas.bbox("all"))
            else:
                messagebox.showinfo("Transactions", "No transaction history available.")

        tk.Button(account_window, text="View Portfolio", command=view_portfolio).pack(pady=5)
        tk.Button(account_window, text="Deposit", command=deposit).pack(pady=5)
        tk.Button(account_window, text="Withdraw", command=withdraw).pack(pady=5)
        tk.Button(account_window, text="View Transaction History", command=view_transaction_history).pack(pady=5)

    tk.Button(dashboard, text="Account Details", command=account_details_window).pack(pady=5)

    # Logout Button
    def handle_logout():
        dashboard.destroy()
        login_window()

    tk.Button(dashboard, text="Logout", command=handle_logout).pack(pady=10)

    dashboard.mainloop()

if __name__ == "__main__":
    login_window()
