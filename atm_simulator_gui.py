import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

class ATMSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Simulator")
        self.root.geometry("300x400")

        self.conn = sqlite3.connect('atm_users.db')
        self.create_table()

        self.balance = 0
        self.current_user = None

        self.deposit_icon = ImageTk.PhotoImage(Image.open("deposit_icon.jpg").resize((20, 20), Image.LANCZOS))
        self.withdraw_icon = ImageTk.PhotoImage(Image.open("withdraw_icon.jpg").resize((20, 20), Image.LANCZOS))
        self.history_icon = ImageTk.PhotoImage(Image.open("history_icon.jpg").resize((20, 20), Image.LANCZOS))
        self.check_icon = ImageTk.PhotoImage(Image.open("check_icon.jpg").resize((20, 20), Image.LANCZOS))
        self.exit_icon = ImageTk.PhotoImage(Image.open("exit_icon.jpg").resize((20, 20), Image.LANCZOS))

        self.languages = {
            "English": {
                "username": "Username:",
                "pin": "PIN:",
                "login": "Login",
                "register": "Register",
                "atm_menu": "ATM Menu",
                "check_balance": "Check Balance",
                "deposit_money": "Deposit Money",
                "withdraw_money": "Withdraw Money",
                "transaction_history": "View Transaction History",
                "view_graph": "View Transaction Graph",
                "exit": "Exit",
                "success": "Success",
                "error": "Error",
                "invalid_credentials": "Invalid credentials.",
                "registration_success": "Registration successful!",
                "username_exists": "Username already exists.",
                "balance": "Your current balance is: $",
                "deposit_prompt": "Enter amount to deposit:",
                "withdraw_prompt": "Enter amount to withdraw:",
                "invalid_withdraw": "Invalid withdrawal amount.",
                "no_transactions": "No transactions found."
            },
            "Arabic": {
                "username": "اسم المستخدم:",
                "pin": "الرقم السري:",
                "login": "تسجيل الدخول",
                "register": "تسجيل",
                "atm_menu": "قائمة الصراف الآلي",
                "check_balance": "التحقق من الرصيد",
                "deposit_money": "إيداع ",
                "withdraw_money": "سحب ",
                "transaction_history": "عرض سجل المعاملات",
                "view_graph": "عرض الرسم البياني للمعاملات",
                "exit": "خروج",
                "success": "تمت العملية بنجاح",
                "error": "خطأ",
                "invalid_credentials": "بيانات غير صحيحة.",
                "registration_success": "تم التسجيل بنجاح!",
                "username_exists": "اسم المستخدم موجود بالفعل.",
                "balance": "رصيدك الحالي هو: $",
                "deposit_prompt": "أدخل المبلغ للإيداع:",
                "withdraw_prompt": "أدخل المبلغ للسحب:",
                "invalid_withdraw": "مبلغ السحب غير صالح.",
                "no_transactions": "لا توجد معاملات."
            }
        }
        self.selected_language = tk.StringVar(value="English")

        self.create_widgets()

    def create_table(self):
        with self.conn:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS users (
                                    username TEXT PRIMARY KEY,
                                    pin INTEGER,
                                    balance REAL
                                )""")
            self.conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT,
                                    type TEXT,
                                    amount REAL,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (username) REFERENCES users (username)
                                )""")

    def create_widgets(self):
        language_frame = ttk.Frame(self.root)
        language_frame.pack(pady=5)

        self.language_label = ttk.Label(language_frame, text="Select Language:")
        self.language_label.pack(side=tk.LEFT)

        self.language_menu = ttk.Combobox(language_frame, textvariable=self.selected_language, values=list(self.languages.keys()))
        self.language_menu.pack(side=tk.LEFT)
        self.language_menu.bind("<<ComboboxSelected>>", self.update_language)

        self.username_label = ttk.Label(self.root, text=self.languages[self.selected_language.get()]["username"])
        self.username_label.pack(pady=5)

        self.username_entry = ttk.Entry(self.root)
        self.username_entry.pack(pady=5)

        self.pin_label = ttk.Label(self.root, text=self.languages[self.selected_language.get()]["pin"])
        self.pin_label.pack(pady=5)

        self.pin_entry = ttk.Entry(self.root, show="*")
        self.pin_entry.pack(pady=5)

        self.login_button = ttk.Button(self.root, text=self.languages[self.selected_language.get()]["login"], command=self.login)
        self.login_button.pack(pady=20)
        self.bind_button_events(self.login_button)

        self.register_button = ttk.Button(self.root, text=self.languages[self.selected_language.get()]["register"], command=self.register)
        self.register_button.pack(pady=5)
        self.bind_button_events(self.register_button)

    def update_language(self, event=None):
        language = self.languages[self.selected_language.get()]
        self.username_label.config(text=language["username"])
        self.pin_label.config(text=language["pin"])
        self.login_button.config(text=language["login"])
        self.register_button.config(text=language["register"])

    def bind_button_events(self, button):
        button.bind("<Enter>", lambda e: button.config(style='Hover.TButton'))
        button.bind("<Leave>", lambda e: button.config(style='TButton'))
        button.bind("<ButtonPress>", lambda e: button.config(style='Pressed.TButton'))
        button.bind("<ButtonRelease>", lambda e: button.config(style='TButton'))

    def login(self):
        username = self.username_entry.get()
        pin = self.pin_entry.get()

        cursor = self.conn.execute("SELECT balance FROM users WHERE username=? AND pin=?", (username, pin))
        user = cursor.fetchone()

        if user:
            self.balance = user[0]
            self.current_user = username
            self.show_menu()
        else:
            messagebox.showerror(self.languages[self.selected_language.get()]["error"], self.languages[self.selected_language.get()]["invalid_credentials"])

    def register(self):
        username = self.username_entry.get()
        pin = self.pin_entry.get()

        with self.conn:
            try:
                self.conn.execute("INSERT INTO users (username, pin, balance) VALUES (?, ?, ?)", (username, pin, 0))
                messagebox.showinfo(self.languages[self.selected_language.get()]["success"], self.languages[self.selected_language.get()]["registration_success"])
            except sqlite3.IntegrityError:
                messagebox.showerror(self.languages[self.selected_language.get()]["error"], self.languages[self.selected_language.get()]["username_exists"])

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        menu_frame = ttk.Frame(self.root)
        menu_frame.pack(pady=20)

        self.menu_label = ttk.Label(menu_frame, text=self.languages[self.selected_language.get()]["atm_menu"], font=("Arial", 16))
        self.menu_label.pack(pady=10)

        self.check_balance_button = ttk.Button(menu_frame, text=self.languages[self.selected_language.get()]["check_balance"], command=self.check_balance, image=self.check_icon, compound="left")
        self.check_balance_button.pack(pady=5)
        self.bind_button_events(self.check_balance_button)

        self.deposit_button = ttk.Button(menu_frame, text=self.languages[self.selected_language.get()]["deposit_money"], command=self.deposit_money, image=self.deposit_icon, compound="left")
        self.deposit_button.pack(pady=5)
        self.bind_button_events(self.deposit_button)

        self.withdraw_button = ttk.Button(menu_frame, text=self.languages[self.selected_language.get()]["withdraw_money"], command=self.withdraw_money, image=self.withdraw_icon, compound="left")
        self.withdraw_button.pack(pady=5)
        self.bind_button_events(self.withdraw_button)

        self.transaction_history_button = ttk.Button(menu_frame, text=self.languages[self.selected_language.get()]["transaction_history"], command=self.view_transaction_history, image=self.history_icon, compound="left")
        self.transaction_history_button.pack(pady=5)
        self.bind_button_events(self.transaction_history_button)

        self.transaction_graph_button = ttk.Button(menu_frame, text=self.languages[self.selected_language.get()]["view_graph"], command=self.show_transaction_graph)
        self.transaction_graph_button.pack(pady=5)
        self.bind_button_events(self.transaction_graph_button)

        self.exit_button = ttk.Button(menu_frame, text=self.languages[self.selected_language.get()]["exit"], command=self.root.quit, image=self.exit_icon, compound="left")
        self.exit_button.pack(pady=5)
        self.bind_button_events(self.exit_button)

    def check_balance(self):
        messagebox.showinfo("Balance", f"{self.languages[self.selected_language.get()]['balance']} {self.balance}")

    def deposit_money(self):
        amount = simpledialog.askfloat("Deposit", self.languages[self.selected_language.get()]["deposit_prompt"])
        if amount and amount > 0:
            self.balance += amount
            with self.conn:
                self.conn.execute("UPDATE users SET balance=? WHERE username=?", (self.balance, self.current_user))
                self.conn.execute("INSERT INTO transactions (username, type, amount) VALUES (?, ?, ?)", (self.current_user, 'Deposit', amount))
            messagebox.showinfo("Success", f"Deposited: ${amount}")
        else:
            messagebox.showerror("Error", self.languages[self.selected_language.get()]["invalid_withdraw"])

    def withdraw_money(self):
        amount = simpledialog.askfloat("Withdraw", self.languages[self.selected_language.get()]["withdraw_prompt"])
        if amount and amount > 0 and amount <= self.balance:
            self.balance -= amount
            with self.conn:
                self.conn.execute("UPDATE users SET balance=? WHERE username=?", (self.balance, self.current_user))
                self.conn.execute("INSERT INTO transactions (username, type, amount) VALUES (?, ?, ?)", (self.current_user, 'Withdraw', amount))
            messagebox.showinfo("Success", f"Withdrew: ${amount}")
        else:
            messagebox.showerror("Error", self.languages[self.selected_language.get()]["invalid_withdraw"])

    def view_transaction_history(self):
        cursor = self.conn.execute("SELECT type, amount, timestamp FROM transactions WHERE username=?", (self.current_user,))
        transactions = cursor.fetchall()

        if not transactions:
            messagebox.showinfo("Transaction History", self.languages[self.selected_language.get()]["no_transactions"])
            return

        history = "\n".join([f"{t[0]}: ${t[1]} on {t[2]}" for t in transactions])
        messagebox.showinfo("Transaction History", history)

    def show_transaction_graph(self):
        cursor = self.conn.execute("SELECT type, amount, timestamp FROM transactions WHERE username=?", (self.current_user,))
        transactions = cursor.fetchall()

        if not transactions:
            messagebox.showinfo("Transaction History", self.languages[self.selected_language.get()]["no_transactions"])
            return

        dates = []
        amounts = []

        for t in transactions:
            dates.append(datetime.strptime(t[2], "%Y-%m-%d %H:%M:%S"))
            amounts.append(t[1] if t[0] == 'Deposit' else -t[1])

        plt.figure(figsize=(10, 5))
        plt.plot(dates, amounts, marker='o')

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()  

        plt.title('Transaction History')
        plt.xlabel('Date')
        plt.ylabel('Amount ($)')
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  
        plt.grid()

        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = ATMSimulator(root)
    root.mainloop()
