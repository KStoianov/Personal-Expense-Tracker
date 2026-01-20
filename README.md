# 💰 Personal Expense Tracker

A lightweight web application built with Flask and SQLite to help users track their income and expenses with ease.

## 🚀 Features

✅ **User Management**
- Create user profiles
- Secure login/logout system
- Password hashing

✅ **Transaction Management**
- Add income and expense transactions
- Edit and delete transactions
- Record amount, category, date, and description

✅ **Category Management**
- Create custom spending categories
- Edit and delete categories
- Organize transactions by category

✅ **Monthly Summary**
- View total income vs expenses
- Calculate net savings
- Analyze spending by category with percentages

✅ **Search & Filter**
- Filter transactions by date range
- Filter by category or transaction type
- Find transactions quickly

✅ **Data Export**
- Export all transactions to CSV
- Download reports for record-keeping

## 📋 Prerequisites

- Python 3.7+
- pip (Python package manager)

## 🔧 Installation & Setup

1. **Navigate to the project directory:**
   ```bash
   cd "Personal Expense Tracker"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   ```bash
   python database.py
   ```
   This will create the SQLite database (`expense_tracker.db`) with all necessary tables.

## 🏃 Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

3. **Create an account or login with existing credentials**

## 📊 Database Schema

### Tables:
- **users**: Stores user profiles (id, name, email, password, created_at)
- **categories**: Custom spending categories (id, user_id, name, created_at)
- **transactions**: Income/expense records (id, user_id, amount, type, category_id, date, description, created_at)

## 🎯 How to Use

### 1. Register & Login
- Create a new account with your email and password
- Login to access your dashboard

### 2. Create Categories
- Go to "Categories" menu
- Add your custom categories (Food, Travel, Rent, etc.)
- Edit or delete categories as needed

### 3. Add Transactions
- Click "Add Transaction"
- Choose type (Income or Expense)
- Enter amount, select category, date, and description
- Submit to save

### 4. View & Filter Transactions
- Go to "Transactions" to see all your records
- Use filters to find transactions by:
  - Type (Income/Expense)
  - Category
  - Date range

### 5. Monthly Summary
- Check "Summary" for:
  - Total income and expenses
  - Net savings calculation
  - Spending breakdown by category with percentages

### 6. Export Data
- On the Transactions page, click "Export CSV"
- Download your transaction history for backup or analysis

## 🔐 Security Notes

⚠️ **Important**: This is a local development app. For production use:
- Change the `secret_key` in `app.py`
- Use environment variables for sensitive data
- Implement HTTPS
- Add additional input validation
- Consider using a more robust database

## 📁 Project Structure

```
Personal Expense Tracker/
├── app.py                 # Flask application & routes
├── database.py            # Database initialization
├── requirements.txt       # Python dependencies
├── expense_tracker.db     # SQLite database (auto-created)
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_transaction.html
│   ├── edit_transaction.html
│   ├── transactions.html
│   ├── categories.html
│   └── summary.html
└── static/                # CSS & client files
    ├── style.css
    └── (exported CSV files)
```

## 🐛 Troubleshooting

**Q: Database not found**
- A: Run `python database.py` to initialize it

**Q: Port 5000 already in use**
- A: Change the port in `app.py` by modifying `app.run(debug=True, port=5001)`

**Q: Module not found error**
- A: Make sure you ran `pip install -r requirements.txt`

## 📝 Tips

- Use descriptive category names for better organization
- Add descriptions to transactions for future reference
- Export your data regularly for backup
- Check the monthly summary to track spending habits

## 🚀 Future Enhancements

- Recurring transactions
- Budget alerts
- Advanced analytics & charts
- Multi-currency support
- Mobile app version
- Cloud sync feature

## 📄 License

This project is open source and available under the MIT License.

---

**Happy tracking! 💸**
