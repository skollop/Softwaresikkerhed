from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs


import re
import blogpost
import config
import database as db
import userview
import logs



class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.path = "index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        #FOR /
        if self.path == "/":
            event = "GET"
            url = self.path
            ip = self.client_address[0]
            entry = [event, ip, url]
            db.create_logentry(entry)
            self.path = "index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        if self.path == "/logs":
            event = "GET"
            url = self.path
            ip = self.client_address[0]
            entry = [event, ip, url]
            db.create_logentry(entry)
            self.path = "index.html"
            data = db.get_logentries()
            log_integrity = db.verify_log_chain()
            logs.create_logview(data, log_integrity, self)

        if re.match("\/blogposts\/\d*\/?$", self.path): #Regex matcher endelser med eller uden /, men ikke med mere bagefter (fx en comment)
            try:
                blogpost_id = self.path.split("/")[2]
                data = db.get_blogpost_single(blogpost_id)
                comments = db.get_comments_many(blogpost_id)
                blogpost.create_response(data, self, comments)
                event = "GET"
                url = self.path
                ip = self.client_address[0]
                entry = [event, ip, url]
                db.create_logentry(entry)
            except:
                print("Fejl i URL")


        if "slet_log" in self.path:
            print(self.path)
            path, tmp = self.path.split('?', 1)
            qs = parse_qs(tmp)
            log_id = str(qs.get('log_id')[0])
            db.delete_log(log_id)

        if re.match("/blogposts/\d+/comment", self.path):
            blogpostId = self.path.split("/")[2]
            path, tmp = self.path.split('?', 1)
            qs = parse_qs(tmp)
            comment = str(qs.get('comment')[0])
            user = str(qs.get('username')[0])
            #print(user, comment)

            event = f"Comment: {comment} By: {user}"
            url = self.path
            ip = self.client_address[0]
            entry = [event, ip, url]
            db.create_logentry(entry)

            db.create_comment(blogpostId, comment, user)
            self.path = f"/blogposts/{blogpostId}/"


        if "login" in self.path:
            print(self.path)
            path, tmp = self.path.split('?', 1)
            qs = parse_qs(tmp)
            user = str(qs.get('usr')[0])
            password = str(qs.get('pwd')[0])
            print(user, password)
            login_response = db.login(user, password)
            print("response", login_response)
            user_exists = False
            data = None

            if login_response == True:
                user_exists = True
                data = db.get_users()
                userview.create_response(user_exists, data, self)
                event = f"Login Success, user = {user}"
                db.windows_eventlog([event])
            else:
                userview.create_response(user_exists, data, self)
                event = f"Login failed, user = {user}"
                db.windows_eventlog([event])
            ip = self.client_address[0]
            entry = [event, ip, self.path]
            db.create_logentry(entry)


def init_db():
    print("creating tables... ")
    db.create_tables()
    print("creating users... ")
    db.create_users()
    print("creating blogposts... ")
    db.create_blogposts()
    print("creating comments... ")
    db.create_comments()
    print("creating logentries... ")
    db.create_logentries()


if __name__ == "__main__":
    hostname = config.webserver["hostname"]
    serverport = config.webserver["serverport"]

    #init_db()

    webServer = HTTPServer((hostname, serverport), MyServer)
    print("Server started and can be accessed from http://%s:%s" % (hostname, serverport))
    db.windows_eventlog(["Server started"])
    print("Log integrity is: ", db.verify_log_chain())
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
    db.windows_eventlog(["Server stopped"])
