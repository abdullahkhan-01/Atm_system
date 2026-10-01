from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "atm-project-secret-key"

DATABASE = "atm.db"


def get_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """Create tables and add beginner-friendly sample Indian accounts."""
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            account_no TEXT UNIQUE NOT NULL,
            pin TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Sample data is inserted only when the database is empty.
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    if count == 0:
        sample_users = [
            ("Aarav Sharma", "10010001", "1234", 25000),
            ("Priya Patil", "10010002", "2345", 18500),
            ("Rohan Deshmukh", "10010003", "3456", 42000),
            ("Ananya Kulkarni", "10010004", "4567", 12750),
        ]

        conn.executemany(
            "INSERT INTO users (name, account_no, pin, balance) VALUES (?, ?, ?, ?)",
            sample_users
        )

    conn.commit()
    conn.close()


def add_transaction(user_id, transaction_type, amount, description):
    """Save a transaction in the database."""
    conn = get_db()
    conn.execute(
        """
        INSERT INTO transactions
        (user_id, transaction_type, amount, description, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            transaction_type,
            amount,
            description,
            datetime.now().strftime("%d %b %Y, %I:%M %p"),
        ),
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    account_no = request.form.get("account_no", "").strip()
    pin = request.form.get("pin", "").strip()

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE account_no = ? AND pin = ?",
        (account_no, pin),
    ).fetchone()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        return redirect(url_for("dashboard"))

    flash("Invalid account number or PIN.", "error")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("index"))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()

    recent_transactions = conn.execute(
        """
        SELECT * FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        transactions=recent_transactions
    )


@app.route("/withdraw", methods=["POST"])
def withdraw():
    if "user_id" not in session:
        return redirect(url_for("index"))

    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0

    if amount <= 0:
        flash("Please enter a valid withdrawal amount.", "error")
        return redirect(url_for("dashboard"))

    if amount % 100 != 0:
        flash("ATM accepts withdrawal amounts in multiples of ₹100.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()

    if amount > user["balance"]:
        conn.close()
        flash("Insufficient balance.", "error")
        return redirect(url_for("dashboard"))

    new_balance = user["balance"] - amount
    conn.execute(
        "UPDATE users SET balance = ? WHERE id = ?",
        (new_balance, user["id"])
    )
    conn.commit()
    conn.close()

    add_transaction(
        user["id"],
        "Withdrawal",
        amount,
        "Cash withdrawal from ATM"
    )

    flash(f"₹{amount:,.2f} withdrawn successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/deposit", methods=["POST"])
def deposit():
    if "user_id" not in session:
        return redirect(url_for("index"))

    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0

    if amount <= 0:
        flash("Please enter a valid deposit amount.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()

    new_balance = user["balance"] + amount
    conn.execute(
        "UPDATE users SET balance = ? WHERE id = ?",
        (new_balance, user["id"])
    )
    conn.commit()
    conn.close()

    add_transaction(
        user["id"],
        "Deposit",
        amount,
        "Cash deposited into account"
    )

    flash(f"₹{amount:,.2f} deposited successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/transfer", methods=["POST"])
def transfer():
    if "user_id" not in session:
        return redirect(url_for("index"))

    receiver_account = request.form.get("receiver_account", "").strip()

    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0

    if amount <= 0:
        flash("Please enter a valid transfer amount.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()
    sender = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()

    receiver = conn.execute(
        "SELECT * FROM users WHERE account_no = ?", (receiver_account,)
    ).fetchone()

    if not receiver:
        conn.close()
        flash("Receiver account not found.", "error")
        return redirect(url_for("dashboard"))

    if receiver["id"] == sender["id"]:
        conn.close()
        flash("You cannot transfer money to your own account.", "error")
        return redirect(url_for("dashboard"))

    if amount > sender["balance"]:
        conn.close()
        flash("Insufficient balance for this transfer.", "error")
        return redirect(url_for("dashboard"))

    sender_balance = sender["balance"] - amount
    receiver_balance = receiver["balance"] + amount

    conn.execute(
        "UPDATE users SET balance = ? WHERE id = ?",
        (sender_balance, sender["id"])
    )
    conn.execute(
        "UPDATE users SET balance = ? WHERE id = ?",
        (receiver_balance, receiver["id"])
    )
    conn.commit()
    conn.close()

    add_transaction(
        sender["id"],
        "Transfer",
        amount,
        f"Transferred to {receiver['name']} ({receiver['account_no']})"
    )

    add_transaction(
        receiver["id"],
        "Received",
        amount,
        f"Received from {sender['name']} ({sender['account_no']})"
    )

    flash(f"₹{amount:,.2f} transferred successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
