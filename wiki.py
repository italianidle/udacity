import webapp2

from handlers import BaseHandler, Signup
from models import User, Page

class WikiPage(BaseHandler):
    def get(self, path):
        page = Page.by_path(path)
        if page:
            self.render("wiki-page.html", page = page)
        else:
            self.redirect("/wiki/_edit" + path)

class EditPage(BaseHandler):
    def get(self, path):
        if not self.user:
            self.redirect("/wiki/login")
        else:
            page = Page.by_path(path)
            self.render("edit-page.html", page = page)

    def post(self, path):
        if not self.user:
            self.error(400)
            return

        content = self.request.get("content")
        
        page = Page.by_path(path)

        if page:
            page.content = content
        else:
            page = Page.new(path, content)

        page.put()

        self.redirect("/wiki" + path)

class Register(Signup):
    def done(self):
        next_url = self.request.headers.get('referer', '/')

        next_url = str(self.request.get('next_url'))
        if not next_url or next_url.startswith('/login'):
            next_url = '/wiki/'

        user = User.register(self.username, self.password, self.email)
        user.put()
                
        self.login(user)
        self.redirect(next_url)

class Login(BaseHandler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.render("login-form.html", next_url =next_url)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        next_url = str(self.request.get('next_url'))
        if not next_url or next_url.startswith('/login'):
            next_url = '/wiki/'

        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect(next_url)
        else:
            error = "Invalid login!"
            self.render("login-form.html", error = error)
            
class Logout(BaseHandler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.logout()
        self.redirect(next_url)
    
PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([('/wiki/signup', Register),
                               ('/wiki/login', Login),
                               ('/wiki/logout', Logout),
                               ('/wiki/_edit' + PAGE_RE, EditPage),
                               ('/wiki' + PAGE_RE, WikiPage)
                               ], debug = True)
