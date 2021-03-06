from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.context import CryptContext
import requests
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
image_path = ""
communitynameglobal = 0

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

    if request.method == "GET":
        if request.form.get("opdracht"):

            # calls search function and renders results
            return render_template("search.html", resultaat = search())

        if session:
            # checks if user is following communities
            if queries.following():

                # get all images form communities user is following
                images = queries.followingcommunities()
                if images:
                    return render_template("index.html",database = images)

        # if user is not following communities, get all images from communities
        return render_template("index.html", database = image_paths)

    else:
        return render_template("index.html",database = image_paths)

# search function
def search():
    if request.method == "POST":

        # queries database for results and returns that result
        resultaat = queries.searching()
        return resultaat

# lists all communities
@app.route("/communities", methods=["GET", "POST"])
def communities():

    # gets information about all communities
    result = queries.allcommunities()
    if not result:

        # notify user if there are no communities availible
        flash('No communities available')
        return render_template("index.html")

    # shows user results
    else:
        return render_template("communities.html", result = result)

# creates community
@login_required
@app.route("/create", methods=["GET", "POST"])
def create():

    # checks request method
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

# upload images to site
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

            # get path of file
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(request.form.get("community upload"))
            # Insert into database
            queries.uploadimage(path)

            return redirect(url_for('uploaded_file',filename=filename))

    else:
        result = queries.allcommunities()
        return render_template("upload.html", result = result)

# upload file to local storage
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# redirects user to our homepage
@app.route("/")
def homepage():
    return redirect(url_for("index"))

# shows user profile
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

# lets user create profile
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

        # add profile to database
        queries.saveprofile()

        # gets profile from databse
        profiel = queries.profilelookup()

        return render_template("profile.html", profiel = profiel[0])

    return render_template("newprofile.html")

# lets user edit their profile
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

        # updates profile in database
        queries.updateprofile()

        # gets profile from database
        profiel = queries.profilelookup()

        return render_template("profile.html", profiel = profiel[0])

    return render_template("editprofile.html")

# lets user change password
@login_required
@app.route("/password", methods=["GET", "POST"])
def password():

    if request.method == "POST":

        # ensure old password is enterd
        if not request.form.get("password"):
            flash('Please enter your current password')
            return render_template("password.html")

        # ensure new password is entered
        if not request.form.get("new"):
            flash('Please enter your new password')
            return render_template("password.html")

        # ensure password check is entered
        if not request.form.get("rnew"):
            flash('Please enter your retyped new password')
            return render_template("password.html")

        # get old password hash for check
        foundpassword = queries.gethash()

        # checks if old password is correct
        if not pwd_context.verify(request.form.get("password"), foundpassword[0]["hash"]):
            flash('Your entered current password did not match with the one in our database')
            return render_template("password.html")

        # updates password in database
        queries.updatepassword()

        flash('Password succesfuly changed')

        # sends user back to homepage
        return render_template("index.html")

    return render_template("password.html")

# logs in user
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

# image page
@login_required
@app.route("/likes", methods=["GET", "POST"])
def likes():

    if request.method == "GET":

        #Query to see if the user has liked anything
        likjes = queries.likje()

        return render_template("likes.html", likjes = likjes)

    return render_template("likes.html")

@login_required
@app.route("/comments", methods=["GET", "POST"])
def comments():

    if request.method == "GET":

        #Query to see if the user has comments
        commentjes = queries.commentje()


        return render_template("comments.html", commentjes = commentjes)

    return render_template("comments.html")

@login_required
@app.route("/images", methods=["GET", "POST"])
def images():
    global image_path
    if request.form.get("image_btn"):
        if image_path != request.form.get("image_btn"):
            image_path = request.form.get("image_btn")
    likecheck = queries.likecheck(image_path)

    # gets nr of likes for image
    likes = queries.imagelikes(image_path)

    # gets all inormation about image
    title = queries.title(image_path)
    comments = queries.selectcomment(image_path)
    userinfo = queries.selectuser()
    communityupload = queries.getcommunityupload(image_path)

    if request.method == "POST":
        if request.form.get("comment"):
            queries.comment(image_path)
            return redirect(url_for("images"))

        print("hier 1")
        # lets user like the image
        if request.form.get("like"):
            print("hier 2")
            queries.like(image_path)

            # update likes in database
            queries.likes(1, image_path)
            flash('liked')
            return redirect(url_for("images"))

        # if user has liked already, unlike
        if request.form.get('unlike'):
            queries.unlike(image_path)

            # updates likes in database
            queries.likes(-1, image_path)
            flash("removed from likes")
            return redirect(url_for("images"))

    return render_template("images.html", title = title[0], community = communityupload[0]["name"], comments = comments, user = userinfo[0]["username"], image_path=image_path, likecheck = likecheck, likes = likes[0])


@login_required
@app.route("/gifs", methods=["GET", "POST"])
def gifs():

    if request.method == "POST":
        # create an instance of the API class
        api_instance = giphy_client.DefaultApi()
        api_key = 'OG1gYfijbQKdvRqS8I46Wgi7IQBwec0H'
        q = request.form.get("gif")
        limit = 5
        offset = 0
        rating = 'g'
        lang = 'en'
        fmt = 'json'
        i = 0
        gifimages = []

        api_response = api_instance.gifs_search_get(api_key, q, limit=limit, offset=offset, rating=rating, lang=lang, fmt=fmt)
        while i < len(api_response.data):
            gifimages.append(api_response.data[i].images.original.url)
            i = i + 1

        return render_template("loadedgifs.html", gifimages = gifimages)

    return render_template("gifs.html")


# logs out user
@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

# community page
@login_required
@app.route("/community", methods=["GET", "POST"] )
def community():
    global communitynameglobal
    if request.form.get("community_btn"):
        if communitynameglobal != request.form.get("community_btn"):
            communitynameglobal = request.form.get("community_btn")

    # gets images, community info and checks if user is following
    communityid = queries.getcommintyid(communitynameglobal)
    followcheck = queries.followcheck(communityid)
    images = queries.communityimagepath(communityid)
    communityinfo = queries.communityinfo(communityid)

    if request.method == 'POST':
        # lets user follow the community
        if request.form.get('follow'):
            queries.follow(communityid)
            flash('You are now following this community!')
            return redirect(url_for("community"))

        if request.form.get("unfollow"):
            queries.unfollow(communityid)
            flash("You are no longer following this community")
            return redirect(url_for("community"))

        return render_template("community.html",database = images, communityinfo = communityinfo[0], followcheck = followcheck)

    else:
        return render_template("community.html", database = images, communityinfo = communityinfo[0], followcheck = followcheck)


