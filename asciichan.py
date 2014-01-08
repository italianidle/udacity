import webapp2

from google.appengine.ext import db
from common import Handler

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC ")

        self.render("asciichan/front.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
            a.put()

            self.redirect('/asciichan')
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title, art, error)

app = webapp2.WSGIApplication([('/asciichan', MainPage)], debug = True)
