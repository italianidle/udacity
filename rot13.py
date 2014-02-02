import string
import webapp2

from handlers import BaseHandler

def shiftn(c, n):
    if c in string.lowercase:
        return chr(((ord(c)-ord('a')+n)%26+ord('a')))
    if c in string.uppercase:
        return chr(((ord(c)-ord('A')+n)%26+ord('A')))
    return c

def rot13(s):
    return ''.join([shiftn(c, 13) for c in s])

class Rot13Page(BaseHandler):
    def get(self):
        self.render("rot13-form.html")

    def post(self):
        text = self.request.get("text")
        self.render("rot13-form.html", text = rot13(text))

app = webapp2.WSGIApplication([('/unit2/rot13', Rot13Page)
                               ], debug = True)
