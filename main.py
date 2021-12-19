from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from urllib.parse import urlparse, parse_qs

import re
import blogpost
import config
import database as db
import userview


class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        #FOR /
        if self.path == "/":
            self.path = "index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        if re.match("/blogposts/\d*/", self.path):
            try:
                blogpost_id = self.path.split("/")[2]
                data = db.get_blogpost_single(blogpost_id)
                comments = db.get_comments_many(blogpost_id)
                blogpost.create_response(data, self, comments)
            except:
                print("Fejl i URL")

        if re.match("/blogposts/\d+/comment", self.path):
            print(self.path)
            blogpostId = self.path.split("/")[2]
            path, tmp = self.path.split('?', 1)
            qs = parse_qs(tmp)
            comment = str(qs.get('comment')[0])
            user = str(qs.get('username')[0])
            print(user, comment)

            db.create_comment(blogpostId, comment, user)
            self.path = f"/blogposts/{blogpostId}/comment"

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
            if login_response != None:
                user_exists = True
                data = db.get_users()

            userview.create_response(user_exists, data, self)


if __name__ == "__main__":
    hostname = config.webserver["hostname"]
    serverport = config.webserver["serverport"]
    db.create_tables()
    db.create_users()
    db.create_blogposts()
    db.create_comments()

    webServer = HTTPServer((hostname, serverport), MyServer)
    print("Server started and can be accessed from http://%s:%s" % (hostname, serverport))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    blogposts = db.get_users()
    for b in blogposts.fetchall():
        print(b)

    webServer.server_close()
    print("Server stopped.")
