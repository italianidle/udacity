import webapp2
import cgi

html="""
<html>
  <head>
    <title>ROT13</title>
  </head>
<body>
  <form method="post">
    <h2>Enter some text to ROT13:</h2>
    <textarea name="text" rows="4" cols="50">%(text)s</textarea>
    <br>
    <input type="submit">
  </form>
</body>
</html>
"""

def shiftn(c,n):
    if ord(c) in range(ord('a'),ord('z')+1):
        return chr(((ord(c)-ord('a')+n)%26+ord('a')))
    if ord(c) in range(ord('A'),ord('Z')+1):
        return chr(((ord(c)-ord('A')+n)%26+ord('A')))
    return c

def rot13(s):
    return ''.join([shiftn(c,13) for c in s])

class Rot13Handler(webapp2.RequestHandler):
    def write_html(self, text=""):
        self.response.write(html % {"text": cgi.escape(text, quote = True)})

    def get(self):
        self.write_html()

    def post(self):
        text = self.request.get("text")

        self.write_html(rot13(text))

app = webapp2.WSGIApplication([('/unit2/rot13', Rot13Handler)], debug = True)
