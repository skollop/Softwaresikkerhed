import html
from datetime import datetime as time
import win32evtlogutil #pip install pypiwin32
import win32evtlog
import sys
import config
import sqlite3 as sl
import bcrypt
import hashlib

db = config.database["name"]
con = sl.connect(db, isolation_level=None)
pepper = config.encryption["pepper"]

def windows_eventlog(event):
    App_Name = "Softwaresikkerhed eksamen"
    App_Event_ID = 7040
    App_Event_Str = event

    win32evtlogutil.ReportEvent(App_Name, App_Event_ID,
                                eventType=win32evtlog.EVENTLOG_INFORMATION_TYPE,
                                strings=App_Event_Str)

def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password,
                         bcrypt.gensalt(12))


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode() + pepper.encode(), hashed_password.encode())


def create_user(username, password):
    username = username.encode()
    password = password.encode()
    hashed_password = get_hashed_password(password + pepper.encode())
    user = (username,hashed_password.decode())
    con.execute("INSERT INTO users (username, password) VALUES (?, ?)", user)

"""
HJEMMELAVEDE METODER TIL LOGIN
"""
"""
def create_user(username, password):
    password = password.encode()  # fixer TypeError: Strings must be encoded before hashing
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # https://stackoverflow.com/a/5293983
    chars = []
    for i in range(16):
        chars.append(random.choice(ALPHABET))
    salt = "".join(chars)
    salt = salt.encode()
    salted_password = salt + password + pepper.encode()
    # print("salted: ", salted_password)
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    salt = salt.decode()  # for at gemme som streng i db
    user = (username, hashed_password, salt)
    con.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)", user)


def login(username, password):
    username = (username,)
    stored_user = con.execute("SELECT password, salt FROM users WHERE username LIKE ?", username)
    try:
        stored_user = stored_user.fetchone()
        stored_password = str(stored_user[0])
        stored_salt = str(stored_user[1])
        password = stored_salt + password + pepper
        password = password.encode()  # fixer TypeError: Strings must be encoded before hashing
        hashed_password = hashlib.sha256(password).hexdigest()
        return stored_password == hashed_password
    except:
        return None
"""

def login(usr, pwd):
    usr = (usr,)
    hashed_pwd = con.execute("SELECT password FROM users WHERE username LIKE ?", usr)
    hashed_pwd = hashed_pwd.fetchone()
    hashed_pwd = str(hashed_pwd[0])
    pwd = str(pwd)
    return check_password(pwd, hashed_pwd)


def get_logentries():
    logentry = con.execute("SELECT * FROM logentry")
    return logentry.fetchall()


def get_latest_logentry_combinedHash():
    stmt = "SELECT combinedHash FROM logentry ORDER BY id DESC LIMIT 1;"
    latest_log = con.execute(stmt)
    return latest_log.fetchone()[0]


def create_logentry(entry: []):
    latest_logentry_combined_hash = get_latest_logentry_combinedHash()
    entry.insert(0, str(time.now()))
    entry.insert(0, latest_logentry_combined_hash)

    combined_hash = ""
    for i in entry:
        combined_hash = combined_hash + i
    combined_hash = hashlib.sha256(combined_hash.encode()).hexdigest()
    entry.insert(1, combined_hash)
    con.execute(
        "INSERT INTO logentry(previousHash, combinedHash, timestamp, event, ipAddress, URL) VALUES (?,?,?,?,?,?)",
        entry)

def fetch_next_log(log_id, log_entries):
    for index, elem in enumerate(log_entries):
        if (index + 1 < len(log_entries)):
            if(elem[0] == log_id):
                return log_entries[index + 1]

def verify_log_chain():
    all_entries = con.execute("SELECT * FROM logentry").fetchall()
    for entry in all_entries:
        if(entry[0] != 1):
            next_entry = fetch_next_log(entry[0], all_entries)
            combined_hash = entry[1] + entry[3] + entry[4] + entry[5] + entry[6]
            combined_hash = hashlib.sha256(combined_hash.encode()).hexdigest()
            previous_hash = next_entry[1]
            if(combined_hash != previous_hash):
                return False
    return True


def delete_log(log_id):
    stmt = f"DELETE FROM logentry WHERE id = {log_id}"
    con.execute(stmt)


def create_comment(blogpostId, bodyText, username):
    bodyText = html.escape(bodyText)
    username = html.escape(username)
    stmt = "INSERT INTO COMMENTS (bodyText, username, blogpostId) VALUES ('" + \
           bodyText + "', '" + username + "', '" + blogpostId + "')"
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
    users = """CREATE TABLE USERS (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL, 
                        salt TEXT);"""
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
    logentry = """CREATE TABLE logentry(
                     id INTEGER PRIMARY KEY,
                     previousHash TEXT NOT NULL,
                     combinedHash TEXT NOT NULL, 
                     timestamp TEXT NOT NULL,
                     event TEXT NOT NULL,
                     ipAddress TEXT NOT NULL,
                     URL TEXT NOT NULL);
                     """
    try:
        con.execute(users)
        con.execute(blogposts)
        con.execute(comment)
        con.execute(logentry)
    except sl.OperationalError as e:
        print(e)
        print("Tabeller findes allerede")


def create_users():
    users = [("Hans Hansen", "123456"),
             ("Bodil Bodilsen", "password123"),
             ("Knud Knudsen", "yZ3Pvx7d9jpQvERbEHBk"),
             ("test", "test")
             ]
    for user in users:
        create_user(user[0], user[1])


def create_blogposts():
    posts = [("test", time.now(), "KATTE ER DE SØDESTE DYR", "KATTE ER SØDE, JEG KAN GODT LIDE AT DE ER PELSEDE"),
             ("Hans Hansen", time.now(), "HUNDE ER KATTE OVERLEGNE", "Jeg kan godt lide hunde"),
             ("Bodil Bodilsen", time.now(), "JEG HADER DYR", "DYR ER KLAMME")]

    con.executemany("INSERT INTO blogposts(username, timestamp, header, bodyText) VALUES (?, ?, ?, ?)", posts)


def create_comments():
    comments = [("<script>alert(\"Cross-site-scripting er træls\")</script>", "Hans Hansen", 1), ("Jeg kan godt lide krabber", "Bodil Bodilsen", 1),
                ("Men hvad med marsvin?", "Hans Hansen", 1),
                ("KATTE LUGTER", "Hans Hansen", 2), ("Jeg kan godt lide krabber", "Bodil Bodilsen", 2),
                ("Men hvad med marsvin?", "Hans Hansen", 2),
                ("KATTE LUGTER", "Hans Hansen", 3), ("Jeg kan godt lide krabber", "Bodil Bodilsen", 3),
                ("Men hvad med marsvin?", "Hans Hansen", 3)]

    con.executemany("INSERT INTO COMMENTS( bodyText, username, blogpostId) VALUES (?,?,?)", comments)


def get_latest_logentry():
    stmt = "SELECT * FROM logentry ORDER BY id DESC LIMIT 1;"
    latest_log = con.execute(stmt)
    return latest_log.fetchone()[0]


def get_logentries():
    logentry = con.execute("SELECT * FROM logentry")
    return logentry


def get_latest_logentry_combinedHash():
    stmt = "SELECT combinedHash FROM logentry ORDER BY id DESC LIMIT 1;"
    latest_log = con.execute(stmt)
    return latest_log.fetchone()[0]


def create_logentry(entry: []):
    latest_logentry_combined_hash = get_latest_logentry_combinedHash()
    entry.insert(0, str(time.now()))
    entry.insert(0, latest_logentry_combined_hash)

    combined_hash = ""
    for i in entry:
        combined_hash = combined_hash + i
    combined_hash = hashlib.sha256(combined_hash.encode()).hexdigest()
    entry.insert(1, combined_hash)
    con.execute(
        "INSERT INTO logentry(previousHash, combinedHash, timestamp, event, ipAddress, URL) VALUES (?,?,?,?,?,?)",
        entry)


def create_logentries():
    previous_hash = hashlib.sha256("FIRST ENTRY".encode()).hexdigest()
    first_entry = (previous_hash, str(time.now()), "FIRST ENTRY", "FIRST ENTRY", "FIRST ENTRY")
    combined_hash = ""
    for i in first_entry:
        combined_hash = combined_hash + i

    combined_hash = hashlib.sha256(combined_hash.encode()).hexdigest()
    first_entry = (previous_hash, combined_hash, str(time.now()), "FIRST ENTRY", "FIRST ENTRY", "FIRST ENTRY")
    con.execute(
        "INSERT INTO logentry(previousHash, combinedHash, timestamp, event, ipAddress, URL) VALUES (?,?,?,?,?,?)",
        first_entry)

    entry = ["GET", "127.0.0.1", "/blogposts/1/"]
    create_logentry(entry)
    entry = ["POST", "127.0.0.2", "/blogposts/2/"]
    create_logentry(entry)
