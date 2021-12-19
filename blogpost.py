def create_response(data, self, comments):
    self.send_response(200)
    self.send_header("Content-type", "text/html, charset=\"UTF-8\"")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>Blog</title></head>", "utf-8"))
    print(data[1])
    self.wfile.write(bytes(f"<p>Indlægget er skrevet af {data[1]} og posted {data[2]}:</p>", "utf-8"))
    self.wfile.write(bytes(f"<h1>{data[3]}</h1>", "utf-8"))
    self.wfile.write(bytes(f"<h2>{data[4]}</h2>", "utf-8"))

    #Kommentarfelt
    self.wfile.write(bytes(f"<p>Kommentarer til opslaget:</p>", "utf-8"))
    for t in comments:
        self.wfile.write(bytes(f"<p>Indlægget er skrevet af {t[2]}\n:</p>", encoding="utf-8"))
        self.wfile.write(bytes(f"<h3>{t[1]}</h3>", encoding='utf-8'))
    self.wfile.write(bytes("<body>", "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))

    #Skriv kommentar
    self.wfile.write(bytes(f"<h2>Skriv en ny kommentar:</h2>", "utf-8"))
    self.wfile.write(bytes(f"<form action=\"/blogposts/{data[0]}/comment\" method=\"get\">", "utf-8"))

    self.wfile.write(bytes("<label for=\"comment\"> Your Comment :</label><br>", "utf-8")) #Label
    self.wfile.write(bytes("<input type=\"text\" id=\"comment\" name=\"comment\"><br>", "utf-8")) #Textfelt

    self.wfile.write(bytes("<label for=\"username\"> Your username :</label><br>", "utf-8"))  # Label
    self.wfile.write(bytes("<input type=\"text\" id=\"username\" name=\"username\"><br>", "utf-8"))  # Textfelt

    self.wfile.write(bytes("<input type=\"submit\" value=\"Submit\"/>", "utf-8")) #Submit-knap
    self.wfile.write(bytes("</form>", "utf-8"))

