# ui.py
import tkinter as tk
from tkinter import messagebox
import db

class MoneyMateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MoneyMate - Personal Finance Manager")
        self.root.geometry("400x400")
        self.root.configure(bg="#f0f0f0")

        # Create UI elements
        self.create_widgets()

        # Initialize balance
        self.update_balance()

    def create_widgets(self):
        # Title
        self.title_label = tk.Label(self.root, text="MoneyMate", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        # Frame for transaction inputs
        self.input_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.input_frame.pack(pady=10)

        # Transaction type
        self.type_label = tk.Label(self.input_frame, text="Transaction Type", bg="#f0f0f0")
        self.type_label.grid(row=0, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar(value="Income")
        self.type_income = tk.Radiobutton(self.input_frame, text="Income", variable=self.type_var, value="Income", bg="#f0f0f0")
        self.type_expense = tk.Radiobutton(self.input_frame, text="Expense", variable=self.type_var, value="Expense", bg="#f0f0f0")
        self.type_income.grid(row=0, column=1, padx=5, pady=5)
        self.type_expense.grid(row=0, column=2, padx=5, pady=5)

        # Category
        self.category_label = tk.Label(self.input_frame, text="Category", bg="#f0f0f0")
        self.category_label.grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = tk.Entry(self.input_frame)
        self.category_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Amount
        self.amount_label = tk.Label(self.input_frame, text="Amount", bg="#f0f0f0")
        self.amount_label.grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.input_frame)
        self.amount_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        # Add button
        self.add_button = tk.Button(self.input_frame, text="Add Transaction", command=self.add_transaction, bg="#4CAF50", fg="white")
        self.add_button.grid(row=3, column=0, columnspan=3, pady=10)

        # Balance display
        self.balance_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.balance_frame.pack(pady=10)
        self.balance_label = tk.Label(self.balance_frame, text="Balance: $0.00", font=("Helvetica", 14), bg="#f0f0f0")
        self.balance_label.pack()

        # Category listbox
        self.category_listbox = tk.Listbox(self.root)
        self.category_listbox.pack(pady=10)
        self.update_category_listbox()

    def add_transaction(self):
        transaction_type = self.type_var.get()
        category = self.category_entry.get()
        amount = self.amount_entry.get()

        if not category or not amount:
            messagebox.showwarning("Input Error", "Please enter both category and amount.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid amount.")
            return

        db.add_transaction(transaction_type, category, amount)
        self.update_balance()
        self.update_category_listbox()
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def update_balance(self):
        balance = db.get_balance()
        self.balance_label.config(text=f"Balance: ${balance:.2f}")

    def update_category_listbox(self):
        self.category_listbox.delete(0, tk.END)
        categories = db.get_categories()
        for category in categories:
            self.category_listbox.insert(tk.END, category)

if __name__ == "__main__":
    root = tk.Tk()
    app = MoneyMateApp(root)
    root.mainloop()