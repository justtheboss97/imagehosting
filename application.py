from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.context import CryptContext
import datetime
from helpers import *
import queries
import os
import random
import json, urllib
import time
import giphy_client
from giphy_client.rest import ApiException
from pprint import pprint

#Sets upload folders and allowed extensions
UPLOAD_FOLDER = 'static/image_database'
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
            flash('Enter a valid name')
            return render_template("register.html")

        # ensure username was submitted
        if not request.form.get("username"):
            flash('Enter a valid username')
            return render_template("register.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            flash('Enter a password')
            return render_template("register.html")

        # ensure password was submitted
        elif not request.form.get("confirm password"):
            flash('Select a birthday')
            return render_template("register.html")

    else:
        return render_template("register.html")

    #Take the username from the table users, if it exists
    check = queries.checkusername()


    #If check finds a name, return an error
    if check:
        flash('Username already in use')
        return render_template("register.html")

    #Check if passwords match
    if request.form.get("password") != request.form.get("confirm password"):
        flash('Retyped password does not match the first entered password')
        return render_template("register.html")

    #Insert the user, username and hash into the database
    result = queries.register1()

    #login user
    session["user_id"] = result

    return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/index", methods=["GET", "POST"])
def index():

    # Import image path from databse.
    image_paths = queries.imagepath()

    if request.method == "POST":
        return render_template("index.html", database = image_paths)

        return render_template("search.html", resultaat = search())
    else:
        return render_template("index.html",database = image_paths)


def search():
    if request.method == "POST":
        resultaat = queries.searching()
        return resultaat


@app.route("/communities", methods=["GET", "POST"])
def communities():
    result = queries.allcommunities()
    if not result:
        flash('No communities available')
        return render_template("index.html")

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
            flash('must provide a Community Name')
            return render_template("create.html")

    # check if communityname is existant in database
    check = queries.communitycheck()

    # if community name does already exist, return error
    if check:
        flash('Community already exists')
        return render_template("create.html")

    # insert community name, privacy, moderator and description into database
    result = queries.createcommunity()

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

            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Insert into database.

            user = queries.select("users", session["user_id"])
            community = queries.select("communities", request.form.get("community upload"))
            queries.insert("images", (user[0]["username"], session["user_id"], community[0]["name"], community[0]["id"], request.form.get("title"), request.form.get("description"), path))

            queries.uploadimage(path)


            return redirect(url_for('uploaded_file',filename=filename))

    else:
        return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/")
def homepage():
    "startpagina"
    return render_template("index.html")

@login_required
@app.route("/profile", methods=["GET", "POST"])
def profile():

    #select id, name, description, birthday from profile
    profiel = queries.profilelookup()

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
            return render_template("newprofile.html")

        #ensure birthday is entered
        if not request.form.get("birthday"):
            flash('Select a birthday')
            return render_template("newprofile.html")

        #ensure description is entered
        if not request.form.get("profiledescription"):
            flash('Please enter a discription')
            return render_template("newprofile.html")

        queries.saveprofile()

        profiel = queries.profilelookup()

        return render_template("profile.html", profiel = profiel[0])

    return render_template("newprofile.html")

@login_required
@app.route("/editprofile", methods=["GET", "POST"])
def editprofile():

    if request.method == "POST":

        #ensure is name entered
        if not request.form.get("name"):
            flash('Please enter a name')
            return render_template("editprofile.html")

        #ensure birthday is entered
        if not request.form.get("birthday"):
            flash('Select a birthday')
            return render_template("editprofile.html")

        #ensure description is entered
        if not request.form.get("profiledescription"):
            flash('Please enter a discription')
            return render_template("editprofile.html")

        queries.updateprofile()

        profiel = queries.profilelookup()

        return render_template("profile.html", profiel = profiel[0])

    return render_template("editprofile.html")

@login_required
@app.route("/password", methods=["GET", "POST"])
def password():

    if request.method == "POST":

        if not request.form.get("password"):
            flash('Please enter your current password')
            return render_template("password.html")

        if not request.form.get("new"):
            flash('Please enter your new password')
            return render_template("password.html")

        if not request.form.get("rnew"):
            flash('Please enter your retyped new password')
            return render_template("password.html")

        foundpassword = queries.gethash()

        if not pwd_context.verify(request.form.get("password"), foundpassword[0]["hash"]):
            flash('Your entered current password did not match with the one in our database')
            return render_template("password.html")

        queries.updatepassword()

        flash('Password succesfuly changed')

        return render_template("index.html")

    return render_template("password.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash('Must provide username')
            return render_template("login.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            flash('Must provide password')
            return render_template("login.html")

        # query database for username
        rows = queries.logincheck()

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            flash('Invalid username and/or password')
            return render_template("login.html")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@login_required
@app.route("/images", methods=["GET", "POST"])
def images():

    if request.method == "GET":
        '''
        comments = db.execute("SELECT comment FROM comments WHERE imageid = :imageid", imageid = )

        db.execute("SELECT path FROM images WHERE id= :id", id = )
        '''

        return render_template("images.html", comments = comments)

    return render_template("images.html")

@login_required
@app.route("/gifs", methods=["GET", "POST"])
def gifs():

    if request.method == "POST":
        # create an instance of the API class
        api_instance = giphy_client.DefaultApi()
        api_key = 'OG1gYfijbQKdvRqS8I46Wgi7IQBwec0H'
        q = request.form.get("gif")
        limit = 1
        offset = 0
        rating = 'g'
        lang = 'en'
        fmt = 'json'

        api_response = api_instance.gifs_search_get(api_key, q, limit=limit, offset=offset, rating=rating, lang=lang, fmt=fmt)
        pprint(api_response)

        #return render_template("loadedgifs.html", api_response = api_response["data"][0][bitly_url])

    return render_template("gifs.html")




@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))
