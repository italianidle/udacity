import webapp2
from datetime import datetime, timedelta

from google.appengine.api import memcache
from google.appengine.ext import db

from handlers import BaseHandler, Signup
from models import Post, User

def age_set(key, val):
    save_time = datetime.utcnow()
    memcache.set(key, (val, save_time))

def age_get(key):
    r = memcache.get(key)
    if r:
        val, save_time = r
        age = (datetime.utcnow() - save_time).total_seconds()
        age = int(age)
    else:
        val, age = None, 0
    return val, age

def get_posts(update = False):
    q = Post.all().order('-created').fetch(limit = 10)
    key = 'all'
    
    posts, age = age_get(key)
    if posts is None or update:
        posts = list(q)
        age_set(key, posts)
    return posts, age
    
class FrontPage(BaseHandler):
    def get(self):
        posts, age = get_posts()
        if self.format == 'html':
            self.render("blog-front.html", posts=posts, age=age)
        else:
            return self.render_json([p.as_dict() for p in posts])

class Permalink(BaseHandler):
    def get(self, post_id):
        post, age = get_post(post_id)

        if not post:
            self.error(404)
            return
        if self.format == 'html':
            self.render("permalink.html", post=post, age=age)
        else:
            self.render_json(post.as_dict())

def get_post(post_id):
    key = post_id
    post, age = age_get(key)
    if post is None:
        post = Post.by_id(int(post_id))
        age_set(key, post)
    return post, age

class NewPost(BaseHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/blog/login")

    def post(self):
        if not self.user:
            self.redirect("/blog")

        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post.new(subject, content)
            p.put()

            get_posts(True)

            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "Subject and content are required!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class Register(Signup):
    def done(self):
        user = User.register(self.username, self.password, self.email)
        user.put()
                
        self.login(user)
        self.redirect("/blog/welcome")

class Login(BaseHandler):
    def get(self):
        self.render("login-form.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect("/blog/welcome")
        else:
            error = "Invalid login!"
            self.render("login-form.html", error = error)
            
class Logout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect("/blog/signup")

class WelcomePage(BaseHandler):
    def get(self):
        if self.user:
            self.render("welcome.html", username=self.user.name)
        else:
            self.redirect("/blog/signup")

class FlushCache(BaseHandler):
    def get(self):
        memcache.flush_all()
        self.redirect("/blog")

app = webapp2.WSGIApplication([(r'/blog/?(?:.json)?', FrontPage),
                               (r'/blog/([0-9]+)(?:.json)?', Permalink),
                               (r'/blog/newpost', NewPost),
                               (r'/blog/signup', Register),
                               (r'/blog/login', Login),
                               (r'/blog/logout', Logout),
                               (r'/blog/welcome', WelcomePage),
                               (r'/blog/flush', FlushCache)
                               ], debug = True)
