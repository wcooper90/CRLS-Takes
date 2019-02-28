from flask import Flask, render_template, request, session
from flask_session import Session

import datetime
import os
import csv

from psycopg2.extensions import AsIs
from tempfile import mkdtemp
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = "postgres://ijszjvjbdhkmsb:e8f64406c77896ab475c2f73fe8e5e3f187e7251e4e7c99c69c59bc5c1b284e6@ec2-107-20-185-27.compute-1.amazonaws.com:5432/d29knmrbpdbcoc"
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
        db.execute("INSERT INTO users (username, password) VALUES(?, ?)", username, password)
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
            return apology("Just put in the damn username, you fool!", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Just put in the damn password, you fool!", 403)

        username = request.form.get("username")
        print(username)

        # Query database for username

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
