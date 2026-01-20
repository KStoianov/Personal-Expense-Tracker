from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import get_db_connection, init_db
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'

# Initialize database on first run
if not os.path.exists('expense_tracker.db'):
    init_db()

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== User Management ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                          (name, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('register.html', error='Email already exists or error occurred')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==================== Dashboard ====================

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get monthly summary
    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as total_expense
        FROM transactions
        WHERE user_id = ? AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    ''', (user_id,))
    summary = cursor.fetchone()
    
    # Get overall summary (all-time)
    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as total_expense
        FROM transactions
        WHERE user_id = ?
    ''', (user_id,))
    overall_summary = cursor.fetchone()
    
    # Get all months with transactions
    cursor.execute('''
        SELECT DISTINCT strftime('%Y-%m', date) as month
        FROM transactions
        WHERE user_id = ?
        ORDER BY month DESC
    ''', (user_id,))
    months = [row['month'] for row in cursor.fetchall()]
    
    # Get monthly breakdown (income and expenses for each month)
    cursor.execute('''
        SELECT 
            strftime('%Y-%m', date) as month,
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as total_expense
        FROM transactions
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
    ''', (user_id,))
    monthly_breakdown = cursor.fetchall()
    
    # Get recent transactions
    cursor.execute('''
        SELECT t.*, c.name as category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC
        LIMIT 10
    ''', (user_id,))
    recent_transactions = cursor.fetchall()
    
    conn.close()
    
    # Monthly values
    total_income = summary['total_income'] or 0
    total_expense = summary['total_expense'] or 0
    net_savings = total_income - total_expense
    
    # Overall values
    overall_income = overall_summary['total_income'] or 0
    overall_expense = overall_summary['total_expense'] or 0
    overall_savings = overall_income - overall_expense
    
    return render_template('dashboard.html', 
                         total_income=total_income,
                         total_expense=total_expense,
                         net_savings=net_savings,
                         overall_income=overall_income,
                         overall_expense=overall_expense,
                         overall_savings=overall_savings,
                         transactions=recent_transactions,
                         months=months,
                         monthly_breakdown=monthly_breakdown)

# ==================== Category Management ====================

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        cursor.execute('INSERT INTO categories (user_id, name) VALUES (?, ?)',
                      (user_id, category_name))
        conn.commit()
    
    cursor.execute('SELECT * FROM categories WHERE user_id = ?', (user_id,))
    categories_list = cursor.fetchall()
    conn.close()
    
    return render_template('categories.html', categories=categories_list)

@app.route('/category/<int:cat_id>/edit', methods=['POST'])
@login_required
def edit_category(cat_id):
    user_id = session['user_id']
    new_name = request.form.get('category_name')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE categories SET name = ? WHERE id = ? AND user_id = ?',
                  (new_name, cat_id, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('categories'))

@app.route('/category/<int:cat_id>/delete', methods=['POST'])
@login_required
def delete_category(cat_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM categories WHERE id = ? AND user_id = ?', (cat_id, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('categories'))

# ==================== Transaction Management ====================

@app.route('/add-transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        transaction_type = request.form.get('type')
        category_id = int(request.form.get('category_id'))
        date = request.form.get('date')
        description = request.form.get('description')
        
        cursor.execute('''
            INSERT INTO transactions (user_id, amount, type, category_id, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, amount, transaction_type, category_id, date, description))
        conn.commit()
        conn.close()
        
        return redirect(url_for('transactions'))
    
    cursor.execute('SELECT * FROM categories WHERE user_id = ?', (user_id,))
    categories_list = cursor.fetchall()
    conn.close()
    
    return render_template('add_transaction.html', categories=categories_list)

@app.route('/transactions')
@login_required
def transactions():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get filter parameters
    filter_type = request.args.get('type', '')
    filter_category = request.args.get('category', '')
    filter_start_date = request.args.get('start_date', '')
    filter_end_date = request.args.get('end_date', '')
    
    # Build query with filters
    query = '''
        SELECT t.*, c.name as category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    '''
    params = [user_id]
    
    if filter_type:
        query += ' AND t.type = ?'
        params.append(filter_type)
    
    if filter_category:
        query += ' AND t.category_id = ?'
        params.append(filter_category)
    
    if filter_start_date:
        query += ' AND t.date >= ?'
        params.append(filter_start_date)
    
    if filter_end_date:
        query += ' AND t.date <= ?'
        params.append(filter_end_date)
    
    query += ' ORDER BY t.date DESC'
    
    cursor.execute(query, params)
    transactions_list = cursor.fetchall()
    
    cursor.execute('SELECT * FROM categories WHERE user_id = ?', (user_id,))
    categories_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('transactions.html', 
                         transactions=transactions_list,
                         categories=categories_list,
                         filter_type=filter_type,
                         filter_category=filter_category)

@app.route('/transaction/<int:trans_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(trans_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        transaction_type = request.form.get('type')
        category_id = int(request.form.get('category_id'))
        date = request.form.get('date')
        description = request.form.get('description')
        
        cursor.execute('''
            UPDATE transactions
            SET amount = ?, type = ?, category_id = ?, date = ?, description = ?
            WHERE id = ? AND user_id = ?
        ''', (amount, transaction_type, category_id, date, description, trans_id, user_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('transactions'))
    
    cursor.execute('SELECT * FROM transactions WHERE id = ? AND user_id = ?', (trans_id, user_id))
    transaction = cursor.fetchone()
    
    cursor.execute('SELECT * FROM categories WHERE user_id = ?', (user_id,))
    categories_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_transaction.html', 
                         transaction=transaction,
                         categories=categories_list)

@app.route('/transaction/<int:trans_id>/delete', methods=['POST'])
@login_required
def delete_transaction(trans_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', 
                  (trans_id, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('transactions'))

# ==================== Summary & Analytics ====================

@app.route('/summary')
@login_required
def summary():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current month summary
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions
        WHERE user_id = ? AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    ''', (user_id,))
    monthly_summary = cursor.fetchone()
    
    # Get spending by category
    cursor.execute('''
        SELECT c.name, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.type = 'expense' 
              AND strftime('%Y-%m', t.date) = strftime('%Y-%m', 'now')
        GROUP BY c.name
        ORDER BY total DESC
    ''', (user_id,))
    spending_by_category = cursor.fetchall()
    
    conn.close()
    
    total_income = monthly_summary['total_income'] or 0
    total_expense = monthly_summary['total_expense'] or 0
    net_savings = total_income - total_expense
    
    return render_template('summary.html',
                         total_income=total_income,
                         total_expense=total_expense,
                         net_savings=net_savings,
                         spending_by_category=spending_by_category)

# ==================== Export ====================

@app.route('/export')
@login_required
def export():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.id, t.amount, t.type, c.name as category, t.date, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC
    ''', (user_id,))
    transactions_list = cursor.fetchall()
    conn.close()
    
    # Create CSV
    filename = f'transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join('static', filename)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Amount', 'Type', 'Category', 'Date', 'Description'])
        for trans in transactions_list:
            writer.writerow(trans)
    
    return jsonify({'file': f'/static/{filename}'})

if __name__ == '__main__':
    app.run(debug=True)
