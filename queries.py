from cs50 import SQL

#returns a the result of a select query
def select(table, query):
    db = SQL("sqlite:///icarus.db")
    if table == "users":
        return db.execute("SELECT * FROM users WHERE id = :id", id = query)


    if table == "communities":
        return db.execute("SELECT * FROM communities WHERE id = :id", id = query)

def select_no_login(username):
    db = SQL("sqlite:///icarus.db")
    return db.execute("SELECT * FROM users WHERE username = :username", username = username)
