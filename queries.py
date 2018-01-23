from cs50 import SQL

db = SQL("sqlite:///icarus.db")

# returns a the result of a select query
def select(table, query):

    # returns all information of user query
    if table == "users":
        return db.execute("SELECT * FROM users WHERE id = :id", id = query)

    if table == "communities":

        # returns all information of community query
        if query != "all":
            return db.execute("SELECT * FROM communities WHERE name = :name", name = query)

        # returns name description and private of query community
        else:
            return db.execute("SELECT name, desc, private FROM communities")

    # returns all information of all images from community query
    if table == "images":
        return db.execute("SELECT * FROM images WHERE communties = :communities", communities = query)


# check for username in database
def select_no_login(username):
    return db.execute("SELECT * FROM users WHERE username = :username", username = username)


# insert data in table
# table is the table in which you want to insert written like this: "users"
# values is a tuple of the values that need to be inserted in the order that is specified in the execute command
def insert(table, values):
    if table == "users":
        return db.execute("INSERT INTO users (name, username, hash) VALUES(:name, :username, :hash)", name = values[0], username = values[1], hash = values[2])
    if table == "communities":
        return  db.execute("INSERT INTO communities (name, private, mod, desc) VALUES(:name, :private, :mod, :desc)", name = values[0], private = values[1], mod = values[2], desc = values[3])
    if table == "images":
        return db.execute("INSERT INTO images (user, userid, community, communityid, title, description, path) VALUES(:user, :userid, :community, :communityid, :title, :descrition, :path)", user = values[0], userid = values[1], community = values[2], communityid = values[3], title = values[4], description = values[5], path = values[6])
