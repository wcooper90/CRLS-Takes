import os
import datetime
import csv
import psycopg2
import requests
import json

from flask import Flask, flash, jsonify, redirect, session, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from datetime import date

app = Flask(__name__)

#if not os.getenv("DATABASE_URL"):
    #raise RuntimeError("DATABASE_URL is not set")


# write README
# stuff that comes at the beginning
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# connects with heroku database and creates db
engine = create_engine("postgres://cnfjlelhbsbqdj:43a55fcedde5bbb4f27c30a1a384f18f76600704afaf42ef9d6f07dce82d0b9c@ec2-54-235-134-25.compute-1.amazonaws.com:5432/d3gbkv3egf6krp", pool_size=50)
db = scoped_session(sessionmaker(bind=engine))

# about page route
@app.route("/about")
def about():
    return render_template("about.html")


# home page route
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/takesG")
def takesG():
    takes = db.execute("SELECT * FROM takes")
    return render_template("takesG.html", takes=takes)

@app.route("/blogsG")
def blogsG():
    return render_template("blogsG.html")


# error page route
@app.route("/error")
def error():
    return render_template("error.html")


# register page route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checks to make sure input username is available
        usernames = db.execute("SELECT username FROM users").fetchall()
        for username in usernames:
            if request.form.get("username") == username:
                return render_template("error.html", message="Someone already has that username. Pick another please.")

        # checks that user has entered a username, password, confirmation, and that the confirmation and password are the same
        if not request.form.get("username"):
            return render_template("error.html", message="Enter a username, you fool")
        elif not request.form.get("password"):
            return render_template("error.html", message="Enter a password, you fool")
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="Confirm your password, you fool")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message="Make sure your damn passwords match, you fool")

        # carries out database insertion
        db.execute("INSERT INTO users (username, passwd, dateJoined) VALUES(:username, :password, :date)", {"username": request.form.get("username"), "password": request.form.get("password"), "date": date.today()})
        db.commit()
        return render_template("login.html")
    else:
        return render_template("register.html")


# login route page
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        # makes sure user has entered password and username
        if not request.form.get("username"):
            return render_template("error.html", message="Enter a username, you fool")
        elif not request.form.get("password"):
            return render_template("error.html", message="Enter a username, you fool")

        # checks to make sure account exists and password is correct
        username = db.execute("SELECT username FROM users WHERE username = (:username)", {"username": request.form.get("username")}).fetchall()
        if not username:
            return render_template("error.html", message="Username does not exist")
        password = db.execute("SELECT passwd FROM users WHERE username = (:username)", {"username": request.form.get("username")}).fetchall()
        if password[0][0] != request.form.get("password"):
            return render_template("error.html", message="Incorrect password")

        # logs user in and redirects to profile page
        session["user_id"] = db.execute("SELECT * FROM users WHERE username = (:username)", {"username": request.form.get("username")}).fetchall()[0]["id"]
        return redirect("/profile")
    else:
        return render_template("login.html")


# logout route
@app.route("/logout")
def logout():
    # logs user out and redirects to home page
    session.clear()
    return redirect("/")


# search page route
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # variable for user's keyword(s)
        keyWord = request.form.get("search")
        # returns search page again if user just presses enter
        if keyWord == "":
            return render_template("search.html")

        # arrays collect all possible matches within the database
        returned = []
        all = []
        all.append(db.execute("SELECT * FROM books WHERE author LIKE (:author)", {"author": '%' + keyWord + '%'}).fetchall())
        all.append(db.execute("SELECT * FROM books WHERE yearPublished LIKE (:yp)", {"yp": '%' + keyWord + '%'}).fetchall())
        all.append(db.execute("SELECT * FROM books WHERE title LIKE (:title)", {"title": '%' + keyWord + '%'}).fetchall())
        all.append(db.execute("SELECT * FROM books WHERE isbn LIKE (:isbn)", {"isbn": '%' + keyWord + '%'}).fetchall())
        for i in range(4):
            if all[i]:
                returned.append(all[i])
        # mechanism that allows webpage to return "no matches" if database doesn't have matches
        if not returned:
            matches = 1
        else:
            matches = 0
        # returns the search page, feeding back all possible matches
        return render_template("search.html", returned=returned, matches=matches)
    else:
        return render_template("search.html")


# profile page route
@app.route("/profile")
def profile():
    # collects from database the user's username and the reviews they have made
    username = db.execute("SELECT username FROM users WHERE id = (:id)", {"id": session["user_id"]}).fetchall()[0][0]
    blogs = db.execute("SELECT * FROM blogs WHERE username = (:user)", {"user": username}).fetchall()
    posts = db.execute("SELECT posts FROM users WHERE id = (:id)", {"id": session["user_id"]}).fetchall()[0][0]
    dateJoined = db.execute("SELECT dateJoined FROM users WHERE id = (:id)", {"id": session["user_id"]}).fetchall()[0][0]
    return render_template("profile.html", username=username, posts=posts, dateJoined=dateJoined, blogs=blogs)


# API route
@app.route("/api/<isbn>")
def api(isbn):
    # calculates average rating
    ratings = db.execute("SELECT rating FROM reviews WHERE isbn = (:isbn)", {"isbn": isbn}).fetchall()
    if not ratings:
        return render_template("error.html", message="404 error, isbn not found")
    avgRate = 0
    for rating in ratings:
        avgRate+=rating[0]
    if len(ratings) > 0:
        avgRate = round(avgRate/(len(ratings)), 2)
    # if no ratings exist, return N/A
    else:
        avgRate = "N/A"
    # other necessary data to return in API
    numG = db.execute("SELECT COUNT(*) FROM reviews WHERE isbn = (:isbn)", {"isbn": isbn}).fetchall()[0][0]
    info = db.execute("SELECT * FROM books WHERE isbn = (:isbn)", {"isbn": isbn}).fetchall()[0]
    # format and data to be returned
    data = {
                "title": info[0],
                "author": info[2],
                "year": info[3],
                "isbn": isbn,
                "review_count": numG,
                "average_score": avgRate
            }
    return render_template("api.html", data=data)


# books page route
@app.route("/blogs/<num>", methods=["GET"])
def blogs(num):
    stuff = db.execute("SELECT * FROM blogs WHERE id = (:id)", {"id": num}).fetchall()[0]
    author = stuff[2]
    title = stuff[4]
    blog = stuff[0]
    return render_template("blogs.html", title=title, blog=blog, author=author)


# profile page route
@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        if request.form.get("type") == "blog":
            return redirect("/writeB")
        else:
            return redirect("/writeT")
    else:
        return render_template("write.html")


@app.route("/writeT", methods=["GET", "POST"])
def writeT():
    if request.method == "POST":
        take = request.form.get("take")
        print(take)
        dateposted = datetime.datetime.now()
        username = db.execute("SELECT username FROM users WHERE id = (:id)", {"id": session["user_id"]}).fetchall()[0][0]
        db.execute("INSERT INTO takes (take, username, dateposted) VALUES(:take, :username, :dateposted)",
                    {'take': take, 'username': username, 'dateposted':dateposted})
        db.commit()
        return redirect("/profile")
    else:
        return render_template("writeT.html")


@app.route("/writeB", methods=["GET", "POST"])
def writeB():
    if request.method == "POST":
        username = db.execute("SELECT username FROM users WHERE id = (:id)", {"id": session["user_id"]}).fetchall()[0][0]
        blog = request.form.get("blog")
        bname = request.form.get("blogN")
        date = datetime.datetime.now()
        bType = request.form.get("type")
        db.execute("INSERT INTO blogs (blog, username, dateposted, bname, typeb) VALUES(:blog, :username, :date, :bname, :typeb)",
                    {'blog': blog, 'username': username, 'date':date, 'bname': bname, 'typeb': bType})
        db.execute("UPDATE users SET posts=posts+1 WHERE id = (:id)", {"id": session["user_id"]})
        db.commit()
        return redirect("/profile")
    else:
        return render_template("writeB.html")


@app.route("/bm", methods=["GET"])
def bm():
    blogs = db.execute("SELECT * FROM blogs WHERE typeb = (:type)", {"type": "Mass News"})
    return render_template("blogsDisplay.html", blogs=blogs, type="Mass News")

@app.route("/bp", methods=["GET"])
def bp():
    blogs = db.execute("SELECT * FROM blogs WHERE typeb = (:type)", {"type": "Pop"})
    return render_template("blogsDisplay.html", blogs=blogs, type="Pop")

@app.route("/bs", methods=["GET"])
def bs():
    blogs = db.execute("SELECT * FROM blogs WHERE typeb = (:type)", {"type": "Sports"})
    return render_template("blogsDisplay.html", blogs=blogs, type="Sports")

@app.route("/bf", methods=["GET"])
def bf():
    blogs = db.execute("SELECT * FROM blogs WHERE typeb = (:type)", {"type": "Featured"})
    return render_template("blogsDisplay.html", blogs=blogs, type="Featured")


@app.route("/takes/<num>", methods=["GET"])
def takes(num):
    stuff = db.execute("SELECT * FROM takes WHERE id = (:id)", {"id": num}).fetchall()[0]
    author = stuff[1]
    take = stuff[0]
    print(take)
    return render_template("takes.html", take=take, author=author)

@app.route("/tfc", methods=["GET"])
def tfc():
    takes = db.execute("SELECT * FROM takes WHERE rating = (:rating)", {"rating": 1})
    return render_template("takesDisplay.html", takes=takes, type="Freezing Cold")

@app.route("/tc", methods=["GET"])
def tc():
    takes = db.execute("SELECT * FROM takes WHERE rating = (:rating)", {"rating": 2})
    return render_template("takesDisplay.html", takes=takes, type="Cool")

@app.route("/tl", methods=["GET"])
def tl():
    takes = db.execute("SELECT * FROM takes WHERE rating = (:rating)", {"rating": 3})
    return render_template("takesDisplay.html", takes=takes, type="Lukewarm")

@app.route("/th", methods=["GET"])
def th():
    takes = db.execute("SELECT * FROM takes WHERE rating = (:rating)", {"rating": 4})
    return render_template("takesDisplay.html", takes=takes, type="Hot")

@app.route("/ts", methods=["GET"])
def ts():
    takes = db.execute("SELECT * FROM takes WHERE rating = (:rating)", {"rating": 5})
    return render_template("takesDisplay.html", takes=takes, type="Scalding")
