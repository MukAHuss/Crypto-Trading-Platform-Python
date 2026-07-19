import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from socket import *
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 

# Global constants for server connection
HOST = 'localhost'  # The server address, we use localhost for simplicity and to avoid conflicts  
PORT = 5050  # The server port

# Function to send a request to the server
def send_request(request):
    
    # Sends a request string to the server and receives a response.
    # Uses a socket to communicate with the server.
    
    try:
        # Using a context manager to automatically close the socket
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))  # Establish connection
            client_socket.send(request.encode())  # Send encoded request
            response = client_socket.recv(1024).decode()  # Receive and decode response
            return response.strip()  # Remove any extra spaces or newlines
    except ConnectionRefusedError:
        # Handles cases where the server is not reachable
        return "Error: Unable to connect to the server."
    except Exception as e:
        # Generic exception handler for unforeseen errors
        return f"Error: {e}"

# Function to log in a user
def login(username, password):
    
    # Sends login credentials to the server and returns True if login is successful, otherwise False.
    
    response = send_request(f"login:{username},{password}")
    return response == "True"  # The server responds with "True" on successful login

# Function to create a new user account
def create_account(username, password, balance):
    
    # Sends a request to create a new user account with initial balance and returns True if the account is created successfully, otherwise False.
    
    try:
        balance = float(balance)  # Ensure the balance is a valid number
        response = send_request(f"create_account:{username},{password},{balance}")
        return response == "True"
    except ValueError:
        # Handles invalid balance input (e.g., non-numeric values)
        return False

# Function to get the user's account balance
def get_balance(username):
    
    # Requests the account balance for the specified username.
    return send_request(f"balance:{username}")

# Function to fetch available assets from the server
def get_assets():

    # Retrieves a list of assets (e.g., cryptocurrencies) and their prices from the server and returns a dictionary with asset names as keys and prices as values.
    response = send_request("view_assets")
    try:
        return json.loads(response)  # Parse JSON response into a Python dictionary
    except json.JSONDecodeError:
        # Handles invalid JSON responses
        return {}

# Function to retrieve the user's portfolio
def get_portfolio(username):

    # Fetches the portfolio data for the specified user and returns a list of assets and their quantities.
    response = send_request(f"view_portfolio:{username}")
    try:
        return json.loads(response)  # Parse JSON response into a Python list
    except json.JSONDecodeError:
        return []

# Function to fetch transaction history
def get_transactions(username):
    # Retrieves a user's transaction history from the server and returns a list of transactions, or an empty list if no history is available.

    response = send_request(f"view_transaction:{username}")
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return []

# Login Window
def login_window():
    """
    Displays the login window for the user to enter credentials.
    Includes a button to navigate to the create account screen.
    """
    def handle_login():
        # Handles the login button click by verifying user credentials.

        username = username_entry.get()
        password = password_entry.get()
        if login(username, password):
            root.destroy()  # Close the login window on successful login
            main_dashboard(username)
        else:
            # Displays an error message if login fails
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def handle_create_account():
        
        # Opens a window for creating a new account and takes username, password, and initial balance input.
        
        create_window = tk.Toplevel(root)
        create_window.title("Create Account")
        create_window.configure(bg="#3D3D3D")  # Set background to match the theme

        # Input fields for account creation
        tk.Label(create_window, text="Username:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=0, column=0, pady=5, padx=5)
        new_username_entry = tk.Entry(create_window, font=("Franklin Gothic Heavy", 12), bg="#5A5A5A", fg="White", insertbackground="White")
        new_username_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(create_window, text="Password:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=1, column=0, pady=5, padx=5)
        new_password_entry = tk.Entry(create_window, show="*", font=("Franklin Gothic Heavy", 12), bg="#5A5A5A", fg="White", insertbackground="White")
        new_password_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(create_window, text="Initial Balance:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=2, column=0, pady=5, padx=5)
        initial_balance_entry = tk.Entry(create_window, font=("Franklin Gothic Heavy", 12), bg="#5A5A5A", fg="White", insertbackground="White")
        initial_balance_entry.grid(row=2, column=1, pady=5, padx=5)

        def submit_create_account():
            
            # Handles account creation and provides feedback to the user.
            
            username = new_username_entry.get()
            password = new_password_entry.get()
            balance = initial_balance_entry.get()
            if create_account(username, password, balance):
                # Success message and close the account creation window
                messagebox.showinfo("Success", "Account created successfully!", parent=create_window)
                create_window.destroy()
            else:
                # Error message for invalid input
                messagebox.showerror("Error", "Failed to create account. Ensure all fields are valid.", parent=create_window)

        # Submit button for account creation
        tk.Button(create_window, text="Submit", command=submit_create_account, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White").grid(row=3, column=0, columnspan=2, pady=10)

    # Main login window setup
    root = tk.Tk()
    root.title("MUK's Crypto Platform - Login")
    root.geometry("525x457+700+275")  # Set window size and position
    root.resizable(False, False)  # Disable resizing for a cleaner look

    # Add background image
    background_image = tk.PhotoImage(file="C:\\Users\\hp\\Documents\\Uni\\Professor Santosh\\General\\CourseWork\\CST1510-CW2\\GUI\\GUI_Backdrop.png")
    bg_label = tk.Label(root, image=background_image)
    bg_label.place(relwidth=1, relheight=1)  # Fill the entire window

    # Configure layout for centering widgets
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(5, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(6, weight=1)

    # Title label
    title_label = tk.Label(root, text="MUK's Crypto Platform", font=("Franklin Gothic Heavy", 18), bg="#3D3D3D", fg="White")
    title_label.grid(row=1, column=1, columnspan=5, pady=20)

    # Username input field
    tk.Label(root, text="Username:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=2, column=2, pady=10, padx=10, sticky="e")
    username_entry = tk.Entry(root, font=("Franklin Gothic Heavy", 12), width=23, bg="#5A5A5A", fg="White", insertbackground="White")
    username_entry.grid(row=2, column=3, columnspan=2, pady=10, padx=10, ipadx=3, sticky="w")

    # Password input field
    tk.Label(root, text="Password:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=3, column=2, pady=10, padx=10, sticky="e")
    password_entry = tk.Entry(root, show="*", font=("Franklin Gothic Heavy", 12), width=23, bg="#5A5A5A", fg="White", insertbackground="White")
    password_entry.grid(row=3, column=3, columnspan=2, pady=10, padx=10, ipadx=3, sticky="w")

    # Login button
    login_button = tk.Button(root, text="Login", command=handle_login, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White", width=6, height=1)
    login_button.grid(row=4, column=2, columnspan=3, pady=5)

    # Create account button
    create_acc_button = tk.Button(root, text="Create Account", command=handle_create_account, font=("Franklin Gothic Heavy", 12), bg="#6B6B6B", fg="White", width=13, height=1)
    create_acc_button.grid(row=4, column=3, columnspan=4, pady=5)

    root.mainloop()

    # Create the main window
    root = tk.Tk()
    root.title("MUK's Crypto Platform - Login")
    root.geometry("525x457+700+275")
    root.resizable(False, False)  # Disable resizing for a cleaner look

    # Add background image
    background_image = tk.PhotoImage(file="C:\\Users\\hp\\Documents\\Uni\\Professor Santosh\\General\\CourseWork\\CST1510-CW2\\GUI\\GUI_Backdrop.png")
    bg_label = tk.Label(root, image=background_image)
    bg_label.place(relwidth=1, relheight=1)  # Fill the entire window

    # Configure grid weights for proper centering
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(5, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(6, weight=1)

    # Add a title label
    title_label = tk.Label(
        root, 
        text="MUK's Crypto Platform", 
        font=("Franklin Gothic Heavy", 18), bg="#3D3D3D", fg="White"  # Darker text for contrast
    )
    title_label.grid(row=1, column=1, columnspan=5, pady=20)

    # Username label and entry
    tk.Label(root, text="Username:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=2, column=2, pady=10, padx=10, sticky="e")

    username_entry = tk.Entry(root, font=("Franklin Gothic Heavy", 12), width=23, bg="#5A5A5A", fg="White", insertbackground="White")
    username_entry.grid(row=2, column=3, columnspan=2, pady=10, padx=10, ipadx=3, sticky="w")

    # Password label and entry
    tk.Label(root, text="Password:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=3, column=2, pady=10, padx=10, sticky="e")

    password_entry = tk.Entry(root, show="*", font=("Franklin Gothic Heavy", 12), width=23, bg="#5A5A5A", fg="White", insertbackground="White")
    password_entry.grid(row=3, column=3, columnspan=2, pady=10, padx=10, ipadx=3, sticky="w")

    # Add a Login button
    login_button = tk.Button(root, text="Login", command=handle_login, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White", width=6, height=1)
    login_button.grid(row=4, column=2, columnspan=3, pady=5)

    create_acc_button = tk.Button(root, text="Create Account", command=handle_create_account, font=("Franklin Gothic Heavy", 12), bg="#6B6B6B", fg="White", width=13, height=1)
    create_acc_button.grid(row=4, column=3, columnspan=4, pady=5)

    root.mainloop()

# Main Dashboard
def main_dashboard(username):
    dashboard = tk.Tk()
    dashboard.title("MUK's Crypto Platform - Dashboard")
    dashboard.geometry("813x489+600+275") # Setting screen resolution to match the backdrop. The values after the "+" are for positioning the window to the center.
    dashboard.configure(bg="#3D3D3D")

    background_image = tk.PhotoImage(file="C:\\Users\\hp\\Documents\\Uni\\Professor Santosh\\General\\CourseWork\\CST1510-CW2\\GUI\\Dashboard_Backdrop.png") # To be replaced when running a demo on a personal system
    bg_label = tk.Label(dashboard, image=background_image)
    bg_label.place(relwidth=1, relheight=1)  # Fill the entire window
    # Portfolio Graph Section
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor("#3D3D3D")
    ax.set_facecolor("#3D3D3D")
    canvas = None

    def display_graph():
        nonlocal canvas
        portfolio = get_portfolio(username)
        assets_data = get_assets()

        if not portfolio:
            messagebox.showinfo("Portfolio", "No portfolio data available.", parent=dashboard)
            return

        # Prepare data for the graph
        assets = []
        values = []

        for asset, quantity in portfolio:
            assets.append(asset)
            values.append(quantity * assets_data.get(asset, 0))  # Calculate total value for each asset

        ax.clear()
        ax.bar(assets, values, color="#4CAF50")
        ax.set_title("Portfolio Value Compared to Owned Assets", color="white")
        ax.set_ylabel("Value ($)", color="white")
        ax.set_xlabel("Assets", color="white")
        ax.tick_params(colors="white")

        if not canvas:
            canvas = FigureCanvasTkAgg(fig, master=dashboard)
            canvas.get_tk_widget().place(x=20, y=100)
        canvas.draw()

    # Sidebar for Buttons
    button_frame = tk.Frame(dashboard, bg="#3D3D3D")
    button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=8)

    button_width = 22  # Set uniform button width
    button_height = 2  # Set uniform button height

    # Buttons
    tk.Button(button_frame, text="Refresh Balance", command=lambda: balance_label.config(
        text=f"Account Balance: {get_balance(username)}"),
        font=("Franklin Gothic Heavy", 12), bg="#707070", fg="White",
        width=button_width, height=button_height).pack(pady=5)

    tk.Button(button_frame, text="View Assets", command=lambda: view_assets_window(dashboard),
              font=("Franklin Gothic Heavy", 12), bg="#707070", fg="White",
              width=button_width, height=button_height).pack(pady=5)

    tk.Button(button_frame, text="Portfolio Graph", command=display_graph,
              font=("Franklin Gothic Heavy", 12), bg="#707070", fg="White",
              width=button_width, height=button_height).pack(pady=5)

    # Buy and Sell Buttons in a single frame
    buy_sell_frame = tk.Frame(button_frame, bg="#3D3D3D")
    buy_sell_frame.pack(pady=5)

    tk.Button(buy_sell_frame, text="Buy", command=lambda: buy_asset_window(dashboard), font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White", width=int(20/2), height=button_height).grid(row=0, column=0, padx=5)
    tk.Button(buy_sell_frame, text="Sell", command=lambda: sell_asset_window(dashboard), font=("Franklin Gothic Heavy", 12), bg="#D0006F", fg="White", width=int(20/2), height=button_height).grid(row=0, column=1, padx=5)
    
    # Account Balance
    balance_label = tk.Label(dashboard, text=f"Account Balance: Loading...", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White")
    balance_label.pack(anchor="nw", padx=10, pady=10)

    # Helper functions for sub-windows
    def view_assets_window(parent):
        assets_window = tk.Toplevel(parent)
        assets_window.title("Available Assets")
        assets_window.configure(bg="#3D3D3D")

        assets = get_assets()
        if not assets:
            tk.Label(assets_window, text="No assets available.", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").pack(pady=10)
            return

        table_frame = ttk.Frame(assets_window)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Asset", "Price ($)")
        table = ttk.Treeview(table_frame, columns=columns, show="headings")
        table.heading("Asset", text="Asset")
        table.heading("Price ($)", text="Price ($)")
        table.column("Asset", anchor="w")
        table.column("Price ($)", anchor="e")

        for asset, price in assets.items():
            table.insert("", tk.END, values=(asset, f"${price:.2f}"))

        table.pack(fill=tk.BOTH, expand=True)

    def buy_asset_window(parent):
        buy_window = tk.Toplevel(parent)
        buy_window.title("Buy Asset")
        buy_window.configure(bg="#3D3D3D")

        tk.Label(buy_window, text="Select Asset:", font=("Franklin Gothic Heavy", 12),bg="#3D3D3D", fg="White").grid(row=0, column=0, pady=5, padx=5)
        asset_dropdown = ttk.Combobox(buy_window, values=list(get_assets().keys()))
        asset_dropdown.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(buy_window, text="Quantity:", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").grid(row=1, column=0, pady=5, padx=5)
        quantity_entry = tk.Entry(buy_window, font=("Franklin Gothic Heavy", 12), bg="#5A5A5A", fg="White", insertbackground="White")
        quantity_entry.grid(row=1, column=1, pady=5, padx=5)

        def submit_buy():
            asset = asset_dropdown.get()
            try:
                quantity = float(quantity_entry.get())
                response = send_request(f"buy_asset:{username},{asset},{quantity}")
                messagebox.showinfo("Buy Asset", response, parent=buy_window)
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity.", parent=buy_window)

        tk.Button(buy_window, text="Buy", command=submit_buy, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White").grid(row=2, column=0, columnspan=2, pady=10)

    def sell_asset_window(parent):
        sell_window = tk.Toplevel(parent)
        sell_window.title("Sell Asset")
        sell_window.configure(bg="#3D3D3D")

        tk.Label(sell_window, text="Select Asset:", font=("Franklin Gothic Heavy", 12),bg="#3D3D3D", fg="White").grid(row=0, column=0, pady=5, padx=5)
        asset_dropdown = ttk.Combobox(sell_window, values=list(get_assets().keys()))
        asset_dropdown.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(sell_window, text="Quantity:", font=("Franklin Gothic Heavy", 12),bg="#3D3D3D", fg="White").grid(row=1, column=0, pady=5, padx=5)
        quantity_entry = tk.Entry(sell_window, font=("Franklin Gothic Heavy", 12), bg="#5A5A5A", fg="White", insertbackground="White")
        quantity_entry.grid(row=1, column=1, pady=5, padx=5)

        def submit_sell():
            asset = asset_dropdown.get()
            try:
                quantity = float(quantity_entry.get())
                response = send_request(f"sell_asset:{username},{asset},{quantity}")
                messagebox.showinfo("Sell Asset", response, parent=sell_window)
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity.", parent=sell_window)

        tk.Button(sell_window, text="Sell", command=submit_sell, font=("Franklin Gothic Heavy", 12), bg="#D0006F", fg="White").grid(row=2, column=0, columnspan=2, pady=10)


    # Account Details
    def account_details_window(parent, username):
        account_window = tk.Toplevel(parent)
        account_window.title("Account Details")
        account_window.configure(bg="#3D3D3D")

        tk.Label(account_window, text=f"Details for {username}", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").pack(pady=10)
        
        def view_portfolio_table():
            portfolio_window = tk.Toplevel(account_window)
            portfolio_window.title("Portfolio Details")
            portfolio_window.configure(bg="#3D3D3D")

            portfolio = get_portfolio(username)

            if not portfolio:
                tk.Label(portfolio_window, text="No portfolio data available.", font=("Franklin Gothic Heavy", 12), bg="#3D3D3D", fg="White").pack(pady=10)
                return

            table_frame = ttk.Frame(portfolio_window)
            table_frame.pack(fill=tk.BOTH, expand=True)

            columns = ("Asset", "Quantity")
            table = ttk.Treeview(table_frame, columns=columns, show="headings")
            table.heading("Asset", text="Asset")
            table.heading("Quantity", text="Quantity")

            for asset, quantity in portfolio:
                table.insert("", tk.END, values=(asset, f"{quantity:.2f}"))
            table.pack(fill=tk.BOTH, expand=True)

        def deposit():
            amount = simpledialog.askfloat("Deposit", "Enter amount to deposit:", parent=account_window)
            if amount and amount > 0:
                response = send_request(f"deposit:{username},{amount}")
                messagebox.showinfo("Deposit", response, parent=account_window)

        def withdraw():
            amount = simpledialog.askfloat("Withdraw", "Enter amount to withdraw:", parent=account_window)
            if amount and amount > 0:
                response = send_request(f"withdraw:{username},{amount}")
                messagebox.showinfo("Withdraw", response, parent=account_window)

        def view_transaction_history():
            transactions = get_transactions(username)
            if transactions:
                history_window = tk.Toplevel(account_window)
                history_window.title("Transaction History")
                history_window.configure(bg="#3D3D3D")

                frame = ttk.Frame(history_window)
                frame.pack(fill=tk.BOTH, expand=True)

                columns = ("Asset", "Quantity", "Action", "Date")
                table = ttk.Treeview(frame, columns=columns, show="headings")
                table.heading("Asset", text="Asset")
                table.heading("Quantity", text="Quantity")
                table.heading("Action", text="Action")
                table.heading("Date", text="Date")

                for asset_name, quantity, action, date in transactions:
                    table.insert("", tk.END, values=(asset_name, f"{quantity:.2f}", action, date))

                table.pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showinfo("Transactions", "No transaction history available.", parent=account_window)

        tk.Button(account_window, text="View Portfolio", command=view_portfolio_table, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White").pack(pady=5)
        tk.Button(account_window, text="Deposit", command=deposit, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White").pack(pady=5)
        tk.Button(account_window, text="Withdraw", command=withdraw, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White").pack(pady=5)
        tk.Button(account_window, text="View Transaction History", command=view_transaction_history, font=("Franklin Gothic Heavy", 12), bg="#4CAF50", fg="White").pack(pady=5)
    
    tk.Button(button_frame, text="Account Details", command=lambda: account_details_window(dashboard, username), font=("Franklin Gothic Heavy", 12), bg="#707070", fg="White",width=button_width, height=button_height).pack(pady=5)
    
    # Logout Button
    def handle_logout():
        dashboard.destroy()
        login_window()

    tk.Button(button_frame, text="Logout", command=lambda: [dashboard.destroy(), login_window()], font=("Franklin Gothic Heavy", 12), bg="Red", fg="White",width=button_width, height=button_height).pack(pady=5)
    dashboard.mainloop()

if __name__ == "__main__":
    login_window()