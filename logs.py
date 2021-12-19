import html

def create_logview(data, log_integrity, self):
    self.send_response(200)
    self.send_header("Content-type", "text/html, charset=\"UTF-8\"")
    self.end_headers()
    self.wfile.write(bytes("<body>", "utf-8"))

    #Kommentarfelt
    for t in data:
        self.wfile.write(bytes(f"<p>{t}\n</p>", encoding="utf-8"))

    self.wfile.write(bytes(f"<p>Log integrity is: {log_integrity}\n</p>", encoding="utf-8"))

    self.wfile.write(bytes("<form action=\"/slet_log\" method=\"get\"> ", encoding="utf-8"))
    self.wfile.write(bytes("<label for=\"usr\">Indsæt nummer for loggen du vil slette:</label><br> ", encoding="utf-8"))
    self.wfile.write(bytes("<input type=\"text\" id=\"log_id\" name=\"log_id\"><br> ", encoding="utf8"))
    self.wfile.write(bytes("<input type=\"submit\" value=\"Submit\"/> ", encoding="utf-8"))
    self.wfile.write(bytes("</form> ", encoding="utf-8"))


    self.wfile.write(bytes("</body></html>", "utf-8"))


