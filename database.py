from datetime import datetime as time

import config
import sqlite3 as sl

db = config.database["name"]
con = sl.connect(db)

def login(usr, pwd):
    login = "SELECT * FROM USERS " \
            "WHERE username like '" + usr + "' and " \
            "password like '" + pwd + "'"
    print(login)
    try:
        result = con.execute(login).fetchone()
    except sl.OperationalError as e:
        result = e
    except sl.Warning as e:
        result = e
    finally:
        return result

def create_comment(blogpostId, bodyText, username):
    stmt = "INSERT INTO COMMENTS (bodyText, username, blogpostId) VALUES ('" + \
           bodyText + "', '" + username + "', '" + blogpostId + "')"

    print(stmt)
    con.execute(stmt)

def get_users():
    users = con.execute("SELECT * FROM users")
    return users

def get_blogposts():
    blogposts = con.execute("SELECT * FROM blogposts")
    return blogposts

def get_blogpost_single(id):
    blogposts = "SELECT * FROM BLOGPOSTS WHERE id like '" + id + "'"
    try:
        result = con.execute(blogposts)
    except sl.OperationalError as e:
        result = e
    finally:
        return result.fetchone()

def get_comments():
    blogposts = con.execute("SELECT * FROM comments")
    return blogposts

def get_comments_many(blogpostId):
    comments = "SELECT * FROM comments WHERE blogpostId like '" + blogpostId + "'"
    try:
        result = con.execute(comments)
    except sl.OperationalError as e:
        result = e
    finally:
        return result.fetchall()

################ INIT DATABASE ################
def create_tables():
       users =      """CREATE TABLE USERS (
                     username TEXT PRIMARY KEY,
                     password TEXT NOT NULL);"""
       blogposts = """ CREATE TABLE BLOGPOSTS(
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        timestamp TEXT, 
                        header TEXT NOT NULL,
                        bodyText TEXT NOT NULL);"""
       comment = """CREATE TABLE COMMENTS(
                        id INTEGER PRIMARY KEY,
                        bodyText TEXT NOT NULL,
                        username TEXT NOT NULL, 
                        blogpostId INTEGER NOT NULL);
                        """
       try:
              con.execute(users)
              con.execute(blogposts)
              con.execute(comment)
       except:
              print("Tabeller findes allerede")

def create_users():
       users = [("Hans Hansen", "123456"),
                ("Bodil Bodilsen", "password123"),
                ("Knud Knudsen", "yZ3Pvx7d9jpQvERbEHBk"),
                ("test", "test")
                ]
       con.executemany("INSERT INTO users VALUES (?, ?)", users)


def create_blogposts():
    posts = [("test", time.now(), "KATTE ER DE SØDESTE DYR", "KATTE ER SØDE, JEG KAN GODT LIDE AT DE ER PELSEDE"),
             ("Hans Hansen", time.now(), "HUNDE ER KATTE OVERLEGNE", "Jeg kan godt lide hunde"),
             ("Bodil Bodilsen", time.now(), "JEG HADER DYR", "DYR ER KLAMME")]

    con.executemany("INSERT INTO blogposts(username, timestamp, header, bodyText) VALUES (?, ?, ?, ?)", posts)

def create_comments():
    comments = [( "<script>alert(\"Cross-site-scripting er træls\")</script>", "Hans Hansen", 1), ( "Jeg kan godt lide krabber", "Bodil Bodilsen", 1),( "Men hvad med marsvin?", "Hans Hansen", 1),
                 ( "KATTE LUGTER", "Hans Hansen", 2), ( "Jeg kan godt lide krabber", "Bodil Bodilsen", 2),("Men hvad med marsvin?", "Hans Hansen", 2),
                 ( "KATTE LUGTER", "Hans Hansen", 3), ( "Jeg kan godt lide krabber", "Bodil Bodilsen", 3),( "Men hvad med marsvin?", "Hans Hansen", 3)]

    con.executemany("INSERT INTO COMMENTS( bodyText, username, blogpostId) VALUES (?,?,?)", comments)