import os 
import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from decorate import login_required
import datetime

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY = "dev",
)
app.config.from_prefixed_env()

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///manage.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    # Log user in
    session.clear()

    if request.method == "POST":
        # Check if username is provided
        if not request.form.get("username"):
            return "Please provide username, 403"
        
        # Check if password is provided
        elif not request.form.get("password"):
            return "Please provide password, 403"
        
        # Retrieve user data from the database
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        # Check if the username exists and the password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return ("Invalid username and/or password", 403)
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to the homepage
        return render_template("homepage.html")
    
    # If the user reached the route via GET
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        username = username.strip()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if confirmation != password:
            return ("Password didn't match, Invalid password", 400)
        elif not username:
            return ("Please provide a valid username", 400)
        elif not password:
            return("Please provide a valid password", 400)
        elif not confirmation:
            return ("Please check your password", 400)
        
        hash = generate_password_hash(password)

        try:
            print("Attempting to insert into database")

            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        except ValueError:
            return ("Username already exist", 400)
        return render_template("login.html")

    return render_template("register.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/", methods=["GET", "POST"])
@login_required
def homepage():
    # print("Session data:", session)  # Check session data
    if request.method == "POST":
        description = request.form.get("description")
        amount = request.form.get("amount")
        transaction_type = request.form.get("transaction_type")
        user_id = session.get("user_id")
       
        if not description or not amount or not transaction_type:
            return("Missing required fields", 403)
        
        try:
            amount = float(amount)
        except ValueError:
            return("Invalid amount", 400)
        
        if amount <= 0:
            return ("Amount must be greater than zero", 400)
        
        db.execute("INSERT INTO transactions (user_id, description, amount, type) VALUES (?, ?, ?, ?)",
                    user_id, description, amount, transaction_type)
        return redirect("/")

    return render_template("homepage.html")


@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transactions():
    user_id = session["user_id"]
    if request.method == "POST":
        reset = request.form.get("reset")
        if reset is not None:
            db.execute("DELETE FROM transactions WHERE user_id = ?", user_id)
        return redirect("/transaction")
    transactions = db.execute("SELECT date, description, amount, type FROM transactions where user_id = ? ORDER BY date DESC", 
                              session["user_id"])
    
    return render_template("transaction.html", transactions=transactions)

    
@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    user_id = session["user_id"]

    # Calculate Total Income
    total_income_query = db.execute("SELECT SUM(amount) AS total_income FROM transactions WHERE user_id = ? AND type = 'income'", user_id)
    total_income = total_income_query[0]['total_income'] if total_income_query[0]['total_income'] is not None else 0

    # Calculate Total Expenses
    total_expense_query = db.execute("SELECT SUM(amount) AS total_expense FROM transactions WHERE user_id = ? AND type = 'expense'", user_id)
    total_expense = total_expense_query[0]['total_expense'] if total_expense_query[0]['total_expense'] is not None else 0

    # Calculate Net Balance using a single query
    net_balance_query = db.execute(
        "SELECT (SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'income') - (SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'expense') AS net_balance",
        user_id, user_id
    )
    net_balance = net_balance_query[0]['net_balance'] if net_balance_query[0]['net_balance'] else 0

    # Pass Data to Template
    return render_template("report.html", total_income=total_income, total_expense=total_expense, net_balance=net_balance)

@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    user_id = session["user_id"]
    if request.method == "POST":
        reset = request.form.get("reset") 
        if reset is not None:
            db.execute("DELETE FROM budgets WHERE user_id = ?", user_id)
            return redirect("/budget")

        category = request.form.get("category")
        budget_amount = request.form.get("budget_amount")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        
        # Check for empty fields
        if not category or not budget_amount or not start_date or not end_date:
            return ("Missing required fields", 400)
        
        try:
            budget_amount = float(budget_amount)
        except ValueError:
            return ("Invalid budget amount", 400)
        
        if budget_amount <= 0:
            return ("Invalid Budget Amount", 403)

        db.execute("INSERT INTO budgets (user_id, category, budget_amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                    user_id, category, budget_amount, start_date, end_date)
        return redirect("/budget")
    
    budgets = db.execute("SELECT category, budget_amount, start_date, end_date FROM budgets WHERE user_id = ?", user_id)

    return render_template("budget.html", budgets=budgets)

@app.route("/about", methods = ["GET", "POST"])
@login_required
def about():
    user_id = session["user_id"]
    
    return render_template("about.html")

@app.route("/faqs", methods = ["GET", "POST"])
@login_required
def faqs():
    user_id = session["user_id"]

    return render_template("faqs.html")

if __name__ == '__main__': 
    app.run(debug=True)
