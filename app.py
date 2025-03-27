from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import db
import io
import matplotlib.pyplot as plt
import csv

app = Flask(__name__)
app.secret_key = 'secret'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        db.add_user(username, hashed_password)
        flash('User registered successfully', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.get_user(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login successful', 'success')
            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    user_id = session['user_id']
    balance = db.get_balance(user_id)
    username = session.get('username')
    return render_template('index.html', balance=balance, username=username)

@app.route('/add', methods=['POST'])
@login_required
def add_transaction():
    user_id = session['user_id']
    transaction_type = request.form['type']
    category = request.form['category']
    amount = request.form['amount']

    if not category or not amount:
        return redirect(url_for('index'))

    try:
        amount = float(amount)
    except ValueError:
        return redirect(url_for('index'))

    balance = db.get_balance(user_id)
    if transaction_type == 'Expense' and (amount > balance or not db.check_budget(user_id, category, amount)):
        flash('Expense amount exceeds balance or budgets for this category', 'error')
        return redirect(url_for('index'))

    db.add_transaction(user_id, transaction_type, category, amount)
    return '', 204


@app.route('/balance')
@login_required
def get_balance():
    user_id = session['user_id']
    balance = db.get_balance(user_id)
    return jsonify(balance=balance)

@app.route('/data')
@login_required
def get_data():
    user_id = session['user_id']
    balance = db.get_balance(user_id)
    categories = db.get_categories(user_id)
    return jsonify(balance=balance, categories=categories)

@app.route('/edit/<int:id>')
@login_required
def edit_transaction(id):
    user_id = session['user_id']
    transaction = db.get_transaction(user_id, id)
    return render_template('edit_transaction.html', transaction=transaction)

@app.route('/transactions')
@login_required
def view_transactions():
    user_id = session['user_id']
    transaction_type = request.args.get('type')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    transactions = db.get_all_transactions(user_id)

    if transaction_type:
        transactions = [t for t in transactions if t['type'] == transaction_type]
    if category:
        transactions = [t for t in transactions if t['category'].lower() == category.lower()]
    if start_date:
        transactions = [t for t in transactions if t['date'] >= start_date]
    if end_date:
        transactions = [t for t in transactions if t['date'] <= end_date]

    return render_template('transactions.html', transactions=transactions)

@app.route('/clear_transactions', methods=['POST'])
@login_required
def clear_transactions():
    user_id = session['user_id']
    password = request.form['password']
    user = db.get_user_by_id(user_id)
    if not user or not check_password_hash(user['password'], password):
        flash('Incorrect password', 'error')
        return redirect(url_for('view_transactions'))

    db.clear_all_transactions(user_id)
    return redirect(url_for('view_transactions'))

@app.route('/chart')
@login_required
def chart_page():
    return render_template('chart.html')

@app.route('/chart_image')
@login_required
def chart_image():
    user_id = session['user_id']
    transactions = db.get_all_transactions(user_id)
    income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
    expense = sum(t['amount'] for t in transactions if t['type'] == 'Expense')

    fig, ax = plt.subplots()
    ax.bar(['Income', 'Expense'], [income, expense], color=['#28a745', '#dc3545'])
    ax.set_ylabel('Amount')
    ax.set_title('Income vs. Expense')

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/export')
@login_required
def export_data():
    user_id = session['user_id']
    transactions = db.get_all_transactions(user_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Type', 'Category', 'Amount', 'Date'])
    for transaction in transactions:
        writer.writerow([transaction['id'], transaction['type'], transaction['category'], transaction['amount'], transaction['date']])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='transactions.csv')

@app.route('/budgets')
@login_required
def view_budgets():
    user_id = session['user_id']
    budgets = db.get_budgets(user_id)
    return render_template('budgets.html', budgets=budgets)

@app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    user_id = session['user_id']
    category = request.form['category']
    amount = request.form['amount']
    if not category or not amount:
        return redirect(url_for('view_budgets'))
    try:
        amount = float(amount)
    except ValueError:
        return redirect(url_for('view_budgets'))
    db.add_budget(user_id, category, amount)
    return redirect(url_for('view_budgets'))

@app.route('/delete_budget/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    user_id = session['user_id']
    db.delete_budget(user_id, id)
    return redirect(url_for('view_budgets'))

@app.route('/edit_budget/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_budget(id):
    user_id = session['user_id']
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        if not category or not amount:
            flash('Category and amount are required', 'error')
            return redirect(url_for('edit_budget', id=id))
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount', 'error')
            return redirect(url_for('edit_budget', id=id))
        db.update_budget(user_id, id, category, amount)
        flash('Budget updated successfully', 'success')
        return redirect(url_for('view_budgets'))
    else:
        budget = db.get_budget(user_id, id)
        return render_template('edit_budget.html', budget=budget)

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True)