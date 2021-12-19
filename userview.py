def create_response(user_exists, data, self):
    if user_exists:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Usertable</title></head>", "utf-8"))
        html_part = '<table>'
        self.wfile.write(bytes("<p>You have permission to see the Users table:</p>", "utf-8"))
        for t in data:
            html_part = html_part + '<tr><td>' + str(t) + '</td></tr>'
        html_part = html_part + '</table>'
        self.wfile.write(bytes(html_part, "utf-8"))

    else:
        self.send_response(403)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Forbidden</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>You do not have permission to see the Users table:</p>", "utf-8"))

    self.wfile.write(bytes("<body>", "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))