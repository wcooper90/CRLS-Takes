from flask import Flask, render_template, request, session
from flask_session import Session

import datetime
import os
import csv

from tempfile import mkdtemp
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = "postgres://cnfjlelhbsbqdj:43a55fcedde5bbb4f27c30a1a384f18f76600704afaf42ef9d6f07dce82d0b9c@ec2-54-235-134-25.compute-1.amazonaws.com:5432/d3gbkv3egf6krp"
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

try:
    # suppose the database has been restarted.
    db.execute("SELECT * FROM users")
    db.close()
except:
    print("poopoo")

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/error")
def error():
    return render_template("error.html")

@app.route("/takesG")
def takesG():
    return render_template("takesG.html")

@app.route("/blogsG")
def blogsG():
    return render_template("blogsG.html")

@app.route("/write")
def write():



    return render_template("writeN.html")

@app.route("/scalding")
def scalding():
    return render_template("scalding.html")

@app.route("/popblogs")
def popblogs():
    return render_template("popblogs.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("register.html")
        if not request.form.get("password"):
            return render_template("register.html")
        if not request.form.get("confirmation"):
            return render_template("register.html")
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html")

        password = request.form.get("password")
        print(password)
        username = request.form["username"]
        print(username)

        # registers user into database and logs them in
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", {"username": request.form.get("username"), "hash": request.form.get("password")})
        # change this later
        db.commit()
        return render_template("login.html")
    else:
        return render_template("register.html")


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

        username = request.form.get("username")
        print(username)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = (:username)", {"username": request.form.get("username")})
        print(db.execute("""SELECT * FROM users WHERE username = :username""", username=username))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not request.form.get("password"):
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
