from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from passlib.context import CryptContext

db = SQL("sqlite:///icarus.db")

# register user, saves information in database users
def register1():
    return db.execute("INSERT INTO users (name, username, hash) VALUES(:name, :username, :hash)",
    name = request.form.get("name"), username = request.form.get("username"), hash = pwd_context.hash(request.form.get("password")))

# gets user hash for login
def logincheck():
    return db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

# checks if username exsist while user registers
def checkusername():
    return db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

# gets all images and all information about images
def allimages():
    return db.execute("SELECT * FROM images")

# queries the database for a search
def searching():
    return db.execute("SELECT name, private, desc FROM communities WHERE name = :opdracht", opdracht = request.form.get("opdracht"))

# gets all communities and all information about communities
def allcommunities():
    return db.execute("SELECT * FROM communities")

# checks if community name already exists
def communitycheck():
    return db.execute("SELECT * FROM communities WHERE name = :name", name = request.form.get("name"))

# saves created community in database
def createcommunity():
    return db.execute("INSERT INTO communities (name, private, mod, desc) VALUES(:name, :private, :mod, :desc)",
    name = request.form.get("name"), private = request.form.get("private"), mod = session["user_id"], desc = request.form.get("desc"))

# selects information about user
def selectuser():
    return db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])

# selects information about community
def selectcommunity():
    return db.execute("SELECT * FROM communities WHERE name = :name", name = request.form.get("community upload"))

# saves image information to database
def uploadimage(path):
    community = selectcommunity()
    return db.execute("INSERT INTO images (userid, communityid, title, description, path) VALUES(:userid, :communityid, :title, :description, :path)",
    userid = session["user_id"], communityid = community[0]["id"], title = request.form.get("title"), description = request.form.get("description"), path = path)

# get user profile information
def profilelookup():
    return db.execute("SELECT id, name, birthday, description FROM profile WHERE id = :id", id = session["user_id"])

# saves user profile to database
def saveprofile():
    return db.execute("INSERT INTO profile (id, name, birthday, description) VALUES (:id, :name, :birthday, :description)",
    id = session["user_id"], name = request.form.get("name"), birthday = request.form.get("birthday"), description = request.form.get("profiledescription"))

# get image path for all images
def imagepath():
    return db.execute("SELECT path FROM images")

# updates profile is user saves changes
def updateprofile():
    return db.execute("UPDATE profile SET name = :name, birthday = :birthday, description = :description WHERE id = :id", name= request.form.get("name"), birthday = request.form.get("birthday"), description = request.form.get("profiledescription"), id = session["user_id"])

# gets hash from user
def gethash():
    return db.execute("SELECT hash FROM users WHERE id = :id", id = session["user_id"])

# updates password from user
def updatepassword():
    return db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash = pwd_context.hash(request.form.get("rnew")), id = session["user_id"])

# get image path for all images
# this is still in beta
def communityimagepath():
    return db.execute("SELECT path FROM images WHERE communityid = :communityid", communityid = 8)

# gets all info of community
def communityinfo():
    return db.execute("SELECT * FROM communities WHERE id = :id", id = 8)

# checks if the user follows a community
def followcheck():
    return db.execute("SELECT * FROM members WHERE communityid = :communityid AND userid = :userid", communityid = 8, userid = session["user_id"])

# checks if user is following communites
def following():
    return db.execute("SELECT communityid FROM members WHERE userid = :userid", userid = session["user_id"])

# follows the user to the community
def follow():
    return db.execute("INSERT INTO members (communityid, userid) VALUES(:communityid, :userid)", communityid = 8, userid = session["user_id"])

# unfollows user from community
def unfollow():
    return db.execute("DELETE FROM members WHERE communityid = :communityid AND userid = :userid", communityid = 8, userid= session["user_id"])

# likes the image
def like(image_path):
    return db.execute("INSERT INTO likes (image, id) VALUES(:image, :id)", image = image_path, id = session["user_id"])

# removes like from database
def unlike(image_path):
    return db.execute("DELETE FROM likes WHERE image = :image, id = :id", image = image_path, id = session["user_id"])

# updates likes for images
def likes(x, image_path):
    like = imagelikes(image_path)
    return db.execute("UPDATE images SET likes = :likes WHERE path = :path", likes = like[0]["likes"] + x, path = image_path)

# gets nr of likes for image
def imagelikes(image_path):
    return db.execute("SELECT likes FROM images WHERE path = :path", path =image_path)

# checks if user has liked image
def likecheck(image_path):
    return db.execute("SELECT * FROM likes WHERE image = :image AND id = :id", image = image_path, id = session["user_id"])

# gives all images paths of communities user follows
def followingcommunities():
    communities = following()
    images = []
    for community in communities:
        image = db.execute("SELECT path FROM images WHERE communityid = :communityid", communityid = community["communityid"])
        for path in image:
            images.append(path)
        path = {}
    return images

# insert comment into database
def comment(image_path):
    return db.execute("INSERT INTO comment (id, image, comment) VALUES (:id, :image, :comment)", id = session["user_id"], image = image_path, comment = request.form.get("comment"))

# select all comments form image
def selectcomment(image_path):
    return db.execute("SELECT comment, id FROM comment WHERE image = :image", image = image_path)

# gets community where image is uploaded
def getcommunityupload(image_path):
    commid = db.execute("SELECT communityid FROM images WHERE path = :path", path = image_path)
    return db.execute("SELECT name FROM communities WHERE id = :id", id = commid[0]["communityid"])