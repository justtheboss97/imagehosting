from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.context import CryptContext
import datetime
from helpers import *
import queries
import os

#Sets upload folders and allowed extensions
UPLOAD_FOLDER = 'image_database'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

        # ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name")

        # ensure username was submitted
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

    #Take the username from the table users, if it exists
    check = queries.select_no_login(request.form.get("username"))


    #If check finds a name, return an error
    if check:
        return apology("username already exists")

    #Check if passwords match
    if request.form.get("password") != request.form.get("confirm password"):
        return apology("passwords do not match")

    #Insert the user, username and hash into the database
    result = queries.insert("users", (request.form.get("name"), request.form.get("username"), pwd_context.hash(request.form.get("password"))))
    print(result)

    #login user
    session["user_id"] = result

    return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        images = queries.select("images", "frontpage")
        return render_template("index.html", images)

        return render_template("search.html", resultaat = search())
    else:
        return render_template("index.html")


def search():
    if request.method == "POST":
        opdracht = request.form.get("opdracht")
        resultaat = queries.searching(opdracht)
        return resultaat


@app.route("/communities", methods=["GET", "POST"])
def communities():
    result = queries.select("communities", "all")
    if not result:
        return apology("No communities available at the moment")

    else:
        return render_template("communities.html", result = result)

@login_required
@app.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "GET":
        return render_template("create.html")

    if request.method == "POST":

        # ensure community name was submitted
        if not request.form.get("name"):
            return apology("must provide a Community Name")

    # check if communityname is existant in database
    check = queries.select("communities", request.form.get("name"))

    # if community name does already exist, return error
    if check:
        return apology("Community already exists")

    # insert community name, privacy, moderator and description into database
    result = queries.insert("communities", (request.form.get("name"), request.form.get("private"), session["user_id"], request.form.get("desc")))

    return redirect(url_for("index"))

    return render_template("index.html")

@login_required
@app.route("/upload", methods=["GET", "POST"])
def upload():

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    "Upload page"
    if request.method == "POST":

        # check if the post request has the file part
        if 'images' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['images']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Insert into database.
            user = queries.select("users", session["user_id"])
            community = queries.select("communities", request.form.get("community upload"))
            queries.insert("images", (user[0]["username"], session["user_id"], community[0]["name"], community[0]["id"], request.form.get("title"), request.form.get("description"), filename))

            return redirect(url_for('index',filename=filename))

    else:
        return render_template("upload.html")


@app.route("/")
def homepage():
    "startpagina"
    return render_template("index.html")

@login_required
@app.route("/profile", methods=["GET", "POST"])
def profile():

    #select id, name, description, birthday from profile
    profiel = db.execute("SELECT id, name, description, birthday FROM profile WHERE id = :id", id = session["user_id"])
    print(profiel)

    #if all are available render the profile page
    if profiel:
        return render_template("profile.html", profiel = profiel[0])

    #if not, redirect to create profile page
    return redirect(url_for("newprofile"))


@login_required
@app.route("/newprofile", methods=["GET", "POST"])
def newprofile():

    if request.method == "POST":

        #ensure is name entered
        if not request.form.get("name"):
            flash('Please enter a name')

        #ensure birthday is entered
        if not request.form.get("birthday"):
            flash('Select a birthday')

        #ensure description is entered
        if not request.form.get("profiledescription"):
            flash('Please enter a discription')

        db.execute("INSERT INTO profile (id, name, birthday, description) VALUES (:id, :name, :birthday, :description)", id = session["user_id"],
        name = request.form.get("name"), birthday = request.form.get("birthday"), description = request.form.get("profiledescription"))

        return render_template("index.html")

    return render_template("newprofile.html")


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
