# main.py
import tkinter as tk
import db
import ui

# Initialize the database
db.init_db()

# Start the Tkinter interface
if __name__ == "__main__":
    root = tk.Tk()
    app = ui.MoneyMateApp(root)
    root.mainloop()