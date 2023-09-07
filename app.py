import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, stock_shares

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd


# Custom filter for absolute value
def absolute(value):
    return abs(value)


app.jinja_env.filters["absolute"] = absolute

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    shares = stock_shares(db)
    # initialise variable to store total value of stocks
    total_value = 0
    portfolio = []
    # get all necessary data about the stocks and portfolio
    for company in shares:
        stock = {}

        symbol = company["symbol"]
        shares = company["total_shares"]
        stock_info = lookup(symbol)
        price = stock_info["price"]
        value = shares * price
        total_value += value

        stock["company"] = stock_info["name"]
        stock["symbol"] = symbol
        stock["shares"] = shares
        stock["price"] = price
        stock["value"] = value

        portfolio.append(stock)
    # get users total cash
    cash_data = db.execute("SELECT cash FROM users WHERE id = ?;", session["user_id"])
    cash = cash_data[0]["cash"]
    overall_value = cash + total_value

    # username for title
    name = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])[
        0
    ]["username"]
    title = f"{name}'s Porfolio"
    return render_template(
        "index.html",
        title=title,
        cash=cash,
        total_value=total_value,
        overall_value=overall_value,
        portfolio=portfolio,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        # store relevant variables
        symbol = request.form.get("symbol")
        # Convert shares to integer and check its value
        try:
            shares = int(request.form.get("shares"))
            if shares <= 0:
                raise ValueError
        except ValueError:
            return apology("Invalid number of shares", 400)
        stock = lookup(symbol)

        # check inputs
        if not symbol or not shares or (shares <= 0):
            return apology("Fields left empty and/or incorrect shares", 400)
        # Check if stock exists
        if not stock:
            return apology("Stock does not exist", 400)
        # check if user has enough money
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash_value = cash[0]["cash"]
        if cash_value < (shares * stock["price"]):
            return apology("Transaction cancelled, balance too low", 403)
        # update cash in user database and then record transaction
        balance = cash_value - (shares * stock["price"])
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?;", balance, session["user_id"]
        )
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, stock_price, type) VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            symbol,
            shares,
            stock["price"],
            "Buy",
        )
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ?;", session["user_id"]
    )
    return render_template("history.html", transactions=transactions)


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    if request.method == "POST":
        try:
            deposit = float(request.form.get("money"))
            deposit = round(deposit, 2)
        except ValueError:
            return apology("Invalid cash amount", 403)
        balance_data = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        old_balance = balance_data[0]["cash"]
        balance = old_balance + deposit
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?;", balance, session["user_id"]
        )
        return redirect("/")

    else:
        return render_template("deposit.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        stock_info = lookup(symbol)

        if not stock_info:  # Check if stock info was fetched successfully.
            return apology("Invalid stock symbol.", 400)

        return render_template("quoted.html", stock=stock_info)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username, password, confirmation = (
            request.form.get("username"),
            request.form.get("password"),
            request.form.get("confirmation"),
        )
        # make sure password and username is not empty
        if not username or not password:
            return apology("must provide both username and password", 400)
        # Make sure both password fields are identical
        if password != confirmation:
            return apology("Passwords do not match", 400)
        # check if username is already in use
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if rows:
            return apology("Username already taken", 400)
        hash = generate_password_hash(password)
        user_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
        )
        session["user_id"] = user_id
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    stock = stock_shares(db)
    names = []
    stock_data = {}
    for company in stock:
        names.append(company["symbol"])
        stock_data[company["symbol"]] = company["total_shares"]

    if request.method == "POST":
        # store relevant variables
        symbol = request.form.get("symbol")
        try:
            shares = float(request.form.get("shares"))
        except ValueError:
            return apology("Invalid number of shares", 400)
        stock = lookup(symbol)

        # check inputs
        if not symbol or not shares or (shares <= 0):
            return apology("Fields left empty and/or incorrect shares", 400)
        # Check if stock exists
        if not stock:
            return apology("Stock does not exist", 400)
        # check if user has enough money
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash_value = cash[0]["cash"]
        if stock_data[symbol] < shares:
            return apology("Not enough shares to sell", 400)
        # update cash in user database and then record transaction
        balance = cash_value + (shares * stock["price"])
        shares = -abs(shares)
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?;", balance, session["user_id"]
        )
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, stock_price, type) VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            symbol,
            shares,
            stock["price"],
            "Sell",
        )
        return redirect("/")

    else:
        return render_template("sell.html", names=names)
