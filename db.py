import sqlite3

# init_db_start
def init_db():
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        type TEXT,
        category TEXT,
        amount REAL,
        date TEXT
    )
    ''')
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE transactions ADD COLUMN user_id INTEGER')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        category TEXT,
        amount REAL
    )
    ''')
    cursor.execute("PRAGMA table_info(budgets)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE budgets ADD COLUMN user_id INTEGER')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')
    conn.commit()
    conn.close()
# init_db_end

# transactions_start
def add_transaction(user_id, transaction_type, category, amount):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (user_id, type, category, amount, date)
    VALUES (?, ?, ?, ?, DATE('now'))
    ''', (user_id, transaction_type, category, amount))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type="Income"', (user_id,))
    income = cursor.fetchone()[0] or 0
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type="Expense"', (user_id,))
    expense = cursor.fetchone()[0] or 0
    conn.close()
    return income - expense

def get_categories(user_id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM transactions WHERE user_id = ?', (user_id,))
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_all_transactions(user_id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, type, category, amount, date FROM transactions WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()

    transactions = []
    for row in rows:
        transaction = {
            'id': row[0],
            'type': row[1],
            'category': row[2],
            'amount': row[3],
            'date': row[4]
        }
        transactions.append(transaction)

    return transactions

def get_transaction(user_id, id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions WHERE user_id = ? AND id = ?', (user_id, id))
    transaction = cursor.fetchone()
    conn.close()
    return transaction

def clear_all_transactions(user_id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()

    # Calculate the current balance
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type="Income"', (user_id,))
    income = cursor.fetchone()[0] or 0
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type="Expense"', (user_id,))
    expense = cursor.fetchone()[0] or 0
    remaining_balance = income - expense

    # Clear all transactions
    cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))

    # Insert a new transaction with the remaining balance
    if remaining_balance != 0:
        cursor.execute('''
        INSERT INTO transactions (user_id, type, category, amount, date)
        VALUES (?, ?, ?, ?, DATE('now'))
        ''', (user_id, 'Income' if remaining_balance > 0 else 'Expense', 'Balance Adjustment', remaining_balance))

    conn.commit()
    conn.close()
# transactions_end

# budgets_start
def add_budget(user_id, category, amount):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO budgets (user_id, category, amount) VALUES (?, ?, ?)', (user_id, category, amount))
    conn.commit()
    conn.close()

def get_budgets(user_id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT b.id, b.category, b.amount,
           IFNULL((SELECT SUM(t.amount) FROM transactions t WHERE t.user_id = b.user_id AND t.category = b.category AND t.type = "Expense"), 0) as spent
    FROM budgets b WHERE b.user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_budget(user_id, id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM budgets WHERE user_id = ? AND id = ?', (user_id, id))
    budget = cursor.fetchone()
    conn.close()
    return budget

def update_budget(user_id, id, category, amount):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE budgets
    SET category = ?, amount = ?
    WHERE user_id = ? AND id = ?
    ''', (category, amount, user_id, id))
    conn.commit()
    conn.close()

def check_budget(user_id, category, amount):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT amount FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
    budget = cursor.fetchone()
    if budget:
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND category = ? AND type = "Expense"', (user_id, category))
        total_expense = cursor.fetchone()[0] or 0
        if total_expense + amount > budget[0]:
            return False
    return True

def delete_budget(user_id, id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM budgets WHERE user_id = ? AND id = ?', (user_id, id))
    conn.commit()
    conn.close()
# budgets_end

# users_start
def add_user(username, password):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'id': user[0], 'username': user[1], 'password': user[2]}
    return None

def get_user_by_id(user_id):
    conn = sqlite3.connect('moneymate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'id': user[0], 'username': user[1], 'password': user[2]}
    return None
# users_end