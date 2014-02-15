import webapp2

from handlers import BaseHandler, Signup
from models import User, Page

class WikiPage(BaseHandler):
    def get(self, path):
        v = self.request.get('v')
        page = None
        if v:
            if v.isdigit():
                page = Page.by_id(int(v), path)
            if not page:
                self.error(404)
                return
        else:
            page = Page.by_path(path).get()
        
        if page:
            self.render("wiki-page.html", page = page, path = path)
        else:
            self.redirect("/wiki/_edit" + path)

class EditPage(BaseHandler):
    def get(self, path):
        if not self.user:
            self.redirect("/wiki/login")

        v = self.request.get('v')
        page = None
        if v:
            if v.isdigit():
                page = Page.by_id(int(v), path)
            if not page:
                self.error(404)
                return
        else:
            page = Page.by_path(path).get()

        self.render("edit-page.html", page = page, path = path)

    def post(self, path):
        if not self.user:
            self.error(400)
            return

        content = self.request.get("content")
        old_page = Page.by_path(path).get()

        if not (old_page or content):
            return
        elif not old_page or old_page.content != content:
            page = Page(parent = Page.parent_key(path), content = content)
            page.put()

        self.redirect("/wiki" + path)

class HistoryPage(BaseHandler):
    def get(self, path):
        pages = Page.by_path(path)
        
        if pages:
            self.render("history-page.html", pages = pages, path = path)
        else:
            self.redirect("/wiki/_edit" + path)

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
                               ('/wiki/_history' + PAGE_RE, HistoryPage),
                               ('/wiki/_edit' + PAGE_RE, EditPage),
                               ('/wiki' + PAGE_RE, WikiPage)
                               ], debug = True)
