import webapp2

from handlers import BaseHandler, Signup
from utils import valid_username

class Register(Signup):
    def done(self):
        self.redirect("/unit2/welcome?username=" + self.username)

class Welcome(BaseHandler):
    def get(self):
        username = self.request.get("username")
        if valid_username(username):
            self.render("welcome.html", username = username)
        else:
            self.redirect("/unit2/signup")

app = webapp2.WSGIApplication([('/unit2/signup', Register),
                               ('/unit2/welcome', Welcome)
                               ], debug = True)
