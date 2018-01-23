from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.context import CryptContext
import datetime
from helpers import *
import queries

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///icarus.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("name"):
            return apology("must provide name")

        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure password was submitted
        elif not request.form.get("confirm password"):
            return apology("must confirm password")
    else:
        return render_template("register.html")

    check = queries.select_no_login(request.form.get("username"))
    if check:
        return apology("username already exists")

    #check if passwords match
    if request.form.get("password") != request.form.get("confirm password"):
        return apology("passwords do not match")

    #insert user into database
    result = db.execute("INSERT INTO users (name, username, hash) VALUES(:name, :username, :hash)", name=request.form.get("name"), username=request.form.get("username"), hash=pwd_context.hash(request.form.get("password")))
    print(result)

    #login user
    session["user_id"] = result

    return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/communities", methods=["GET", "POST"])
def communities():
    return render_template("communities.html")


@login_required
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("create.html")

    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide a Community Name")

    check = db.execute("SELECT name FROM communities WHERE name = :name", name = request.form.get("name"))

    if check:
        return apology("Community already exists")

    result = db.execute("INSERT INTO communities (name, private, mod, desc) VALUES(:name, :private, :mod, :desc)", name=request.form.get("name"), private=request.form.get("private"), mod=session["user_id"], desc=request.form.get("desc"))


    return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/")
def homepage():
    "startpagina"
    return render_template("index.html")

@login_required
@app.route("/profile", methods=["GET", "POST"])
def profile():
    return render_template("profile.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = queries.select_no_login(request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))
