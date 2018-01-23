from cs50 import SQL

db = SQL("sqlite:///icarus.db")

#returns a the result of a select query
def select(table, query):
    if table == "users":
        return db.execute("SELECT * FROM users WHERE id = :id", id = query)

    if table == "communities":
        return db.execute("SELECT * FROM communities WHERE name = :name", name = query)

def select_no_login(username):
    return db.execute("SELECT * FROM users WHERE username = :username", username = username)

def insert(table, values):
    if table == "users":
        return db.execute("INSERT INTO users (name, username, hash) VALUES(:name, :username, :hash)", name = values[0], username = values[1], hash = values[2])
