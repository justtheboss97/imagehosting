from cs50 import SQL

db = SQL("sqlite:///icarus.db")

#returns a the result of a select query
def select(table, query):
    if table == "users":
        return db.execute("SELECT * FROM users WHERE id = :id", id = query)

    if table == "communities":
        if query != "all"
            return db.execute("SELECT * FROM communities WHERE name = :name", name = query)
        else:
            return db.execute("SELECT name FROM communities")


def select_no_login(username):
    return db.execute("SELECT * FROM users WHERE username = :username", username = username)

def insert(table, values):
    if table == "users":
        return db.execute("INSERT INTO users (name, username, hash) VALUES(:name, :username, :hash)", name = values[0], username = values[1], hash = values[2])
    if table == "communities":
        return  db.execute("INSERT INTO communities (name, private, mod, desc) VALUES(:name, :private, :mod, :desc)", name = values[0], private = values[1], mod = values[2], desc = values[3])
    if table == "images":
        db.execute("INSERT INTO images ()")
