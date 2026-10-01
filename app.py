from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = "atm123"


users = {
    "10010001": {
        "name": "Aarav Sharma",
        "pin": "1234",
        "balance": 25000,
        "transactions": []
    },
    "10010002": {
        "name": "Priya Patil",
        "pin": "2345",
        "balance": 18500,
        "transactions": []
    },
    "10010003": {
        "name": "Rohan Deshmukh",
        "pin": "3456",
        "balance": 42000,
        "transactions": []
    },
    "10010004": {
        "name": "Ananya Kulkarni",
        "pin": "4567",
        "balance": 12750,
        "transactions": []
    }
}


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        account = request.form["account_no"]
        pin = request.form["pin"]

        if account in users and users[account]["pin"] == pin:

            session["account"] = account
            return redirect("/dashboard")

        flash("Wrong account number or PIN.", "error")

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    if "account" not in session:
        return redirect("/")

    user = users[session["account"]]

    return render_template(
        "dashboard.html",
        user=user,
        transactions=user["transactions"][:5]
    )


@app.route("/deposit", methods=["POST"])
def deposit():

    user = users[session["account"]]
    amount = float(request.form["amount"])

    user["balance"] += amount

    user["transactions"].insert(0, {
        "type": "Deposit",
        "amount": amount,
        "description": "Money deposited"
    })

    flash("Money deposited successfully.", "success")

    return redirect("/dashboard")


@app.route("/withdraw", methods=["POST"])
def withdraw():

    user = users[session["account"]]
    amount = float(request.form["amount"])

    if amount > user["balance"]:

        flash("Insufficient balance.", "error")

    else:

        user["balance"] -= amount

        user["transactions"].insert(0, {
            "type": "Withdrawal",
            "amount": amount,
            "description": "Money withdrawn"
        })

        flash("Money withdrawn successfully.", "success")

    return redirect("/dashboard")


@app.route("/transfer", methods=["POST"])
def transfer():

    sender = users[session["account"]]

    receiver_account = request.form["receiver_account"]
    amount = float(request.form["amount"])

    if receiver_account not in users:

        flash("Account not found.", "error")

    elif receiver_account == session["account"]:

        flash("You cannot transfer to yourself.", "error")

    elif amount > sender["balance"]:

        flash("Insufficient balance.", "error")

    else:

        receiver = users[receiver_account]

        sender["balance"] -= amount
        receiver["balance"] += amount

        sender["transactions"].insert(0, {
            "type": "Transfer",
            "amount": amount,
            "description": "Money transferred"
        })

        flash("Money transferred successfully.", "success")

    return redirect("/dashboard")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
