# check_budgets.py
import sqlite3

def check_budgets():
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM budgets')
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        print(row)

if __name__ == '__main__':
    check_budgets()