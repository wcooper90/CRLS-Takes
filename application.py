from flask import Flask, render_template
import datetime

app = Flask(__name__)

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
