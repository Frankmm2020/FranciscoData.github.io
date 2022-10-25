import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
    ## API key from IEX Cloud:
    ## export API_KEY=pk_4dd25a44c1d0455a9ef9340ebd91bd3d



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

    db.execute("CREATE TABLE IF NOT EXISTS user_? (symbol TEXT NOT NULL, op_price NUMERIC NOT NULL, shares INTEGER NOT NULL, date_time TEXT NOT NULL, current_price NUMERIC, operation TEXT NOT NULL)", session["user_id"])
    """Show portfolio of stocks"""
    stocks_db = db.execute("SELECT symbol, SUM(CASE operation WHEN 'buy' THEN shares WHEN 'sell' THEN -shares END) as shares, current_price FROM user_? GROUP BY symbol HAVING shares > 0", session["user_id"])
    current_cash = (db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"]))[0]['cash']
    grand_total = current_cash
    #update column with current prices
    for row in range(len(stocks_db)):
        tmp_symbol = (stocks_db)[row]['symbol']
        tmp_shares = (stocks_db)[row]['shares']
        tmp_price = (lookup(tmp_symbol))['price']
        db.execute("UPDATE user_? SET current_price = ? WHERE symbol = ?", session["user_id"], tmp_price, tmp_symbol)
        grand_total = grand_total + (tmp_price * tmp_shares)

    return render_template("index.html", current_cash=usd(current_cash), stocks_db=stocks_db, grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    try:
        if request.method == "POST":
            symbol = request.form.get("symbol")
            shares = int(request.form.get("shares"))
            if (shares <= 0):
                return apology("Invalid quantity of shares")
            symbol_looked = lookup(symbol) # dicctionary: {"name": str, "price": float, "symbol": str}
            current_cash = (db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"]))[0]['cash']
            user = session["user_id"]
            stock_price = symbol_looked["price"]
            spent = stock_price * shares
            if spent > current_cash:
                return apology ("Not enough cash")

            db.execute("CREATE TABLE IF NOT EXISTS user_? (symbol TEXT NOT NULL, op_price NUMERIC NOT NULL, shares INTEGER NOT NULL, date_time TEXT NOT NULL, current_price NUMERIC, operation TEXT NOT NULL)", session["user_id"])
            db.execute("INSERT INTO user_? (symbol, op_price, shares, date_time, current_price, operation) VALUES(?,?,?, datetime('now'), ?, ?)", session["user_id"], symbol, stock_price, shares, stock_price, "buy")
            db.execute("UPDATE users SET cash = ? WHERE id = ?", (current_cash - spent), user)

            flash("Share(s) bought!")
            return redirect("/")
            #return apology("you are here")
        else:
            return render_template("buy.html")
    except:
        return apology("Symbol not found")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    db.execute("CREATE TABLE IF NOT EXISTS user_? (symbol TEXT NOT NULL, op_price NUMERIC NOT NULL, shares INTEGER NOT NULL, date_time TEXT NOT NULL, current_price NUMERIC, operation TEXT NOT NULL)", session["user_id"])
    stocks_db = db.execute("SELECT symbol, op_price, shares, operation, date_time FROM user_?", session["user_id"])
    return render_template("history.html", stocks_db=stocks_db)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
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
    try:
        if request.method == "POST":
            symbol = request.form.get("symbol")
            symbol_looked = lookup(symbol) # dicctionary: {"name": str, "price": float, "symbol": str}
            return render_template("quoted.html", symbol_looked=symbol_looked)
        else:
            return render_template("quote.html")
    except:
        return apology("Symbol not found", 400)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must provide password confirmation", 400)
        elif password != confirmation:
            return apology("password didn't match", 400)

        hash1 = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash1)
            return redirect("/")
        except:
            return apology("Username is taken", 400)

    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    db.execute("CREATE TABLE IF NOT EXISTS user_? (symbol TEXT NOT NULL, op_price NUMERIC NOT NULL, shares INTEGER NOT NULL, date_time TEXT NOT NULL, current_price NUMERIC, operation TEXT NOT NULL)", session["user_id"])
    stocks_db = db.execute("SELECT symbol, SUM(CASE operation WHEN 'buy' THEN shares WHEN 'sell' THEN -shares END) as shares, current_price FROM user_? GROUP BY symbol HAVING shares > 0", session["user_id"])
    current_cash = (db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"]))[0]['cash']
    try:
        if request.method == "POST":
            symbol = request.form.get("symbol")
            sell_shares = int(request.form.get("shares"))
            available_shares = int(db.execute("SELECT SUM(CASE operation WHEN 'buy' THEN shares WHEN 'sell' THEN -shares END) as shares FROM user_? GROUP BY symbol HAVING symbol = ?", session["user_id"], symbol)[0]['shares'])
            if sell_shares > available_shares:
                return apology(f"Not enough shares. Only {available_shares} shares available", 400)
            elif sell_shares < 1:
                return apology("Minimum number to sell is 1", 400)

            current_price = (lookup(symbol))['price']
            new_cash = current_cash + (sell_shares * current_price)
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])
            db.execute("INSERT INTO user_? (symbol, op_price, shares, date_time, current_price, operation) VALUES(?,?,?, datetime('now'), ?, ?)", session["user_id"], symbol, current_price, sell_shares, current_price, "sell")
            flash("Share sold!")
            return redirect("/")
        else:
            return render_template("sell.html",stocks_db=stocks_db)
    except:
        return apology("Stock not owned", 400)



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html")




@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    extracash = int(request.form.get("extracash"))
    if extracash <= 0:
        flash("incorrect funds!")
        return redirect("/profile")
    current_cash = float((db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"]))[0]['cash'])
    new_cash = extracash + current_cash
    db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])
    flash("Funds added succesfully")
    return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    old_pass = request.form.get("old_pass")
    new_pass = request.form.get("new_pass")
    user = (db.execute("SELECT * FROM users WHERE id = ?", session["user_id"]))
    if not check_password_hash(user[0]["hash"], old_pass):
        flash("incorrect password!")
        return redirect("/profile")
    hash1 = generate_password_hash(new_pass, method='pbkdf2:sha256', salt_length=8)
    db.execute("UPDATE users SET hash = ? WHERE id = ?", hash1, session["user_id"])
    flash("Password changed!")
    return redirect("/")