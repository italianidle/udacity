import webapp2

from google.appengine.ext import db
from common import BaseHandler

import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PWD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PWD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)


class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()

class MainPage(BaseHandler):
    def render_front(self):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC ")

        self.render("blog/front.html", posts=posts)

    def get(self):
        self.render_front()

class NewPost(BaseHandler):
    def render_page(self, subject="", content="", error=""):
        self.render("blog/newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_page()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = Post(subject = subject, content = content)
            post.put()

            self.redirect("/blog/%d" % post.key().id())
        else:
            error = "Subject and content are required!"
            self.render_page(subject, content, error)

class Permalink(BaseHandler):
    def render_page(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render("blog/front.html", posts=[post])

    def get(self, post_id):
        self.render_page(post_id)

class Signup(BaseHandler):
    def render_page(self, username="", email="", username_error="", password_error="", verify_error="", email_error=""):
        self.render("blog/signup.html", username=username, email=email, 
                    username_error=username_error, password_error=password_error, verify_error=verify_error, email_error=email_error)

    def get(self):
        self.render_page()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        username_error = ""
        password_error = ""
        verify_error = ""
        email_error = ""

        if not valid_username(username):
            username_error = "That's not a valid username."

        if password == verify:
            if not valid_password(password):
                password_error = "That wasn't a valid password."
        else:
            verify_error = "Your passwords didn't match."      
        
        if email and not valid_email(email):
            email_error = "That's not a valid email."

        if username_error or password_error or verify_error or email_error:
            self.render_page(username, email, username_error, password_error, verify_error, email_error)
        else:
            user = User(username=username, password=password, email=email)
            user.put()

            self.set_secure_cookie('user_id', str(user.key().id()))
            self.redirect("/blog/welcome")


class WelcomePage(BaseHandler):

    def get(self):
        cookie_val = self.read_secure_cookie('user_id')

        if cookie_val:
            user_id = int(cookie_val)
            user = User.get_by_id(user_id)
            
            username = user.username
            self.render("blog/welcome.html", username=username)
        else:
            self.set_secure_cookie('user_id','')
            self.redirect("/blog/signup")


app = webapp2.WSGIApplication([(r'/blog/?', MainPage),
                               (r'/blog/newpost', NewPost),
                               (r'/blog/(\d+)', Permalink),
                               (r'/blog/signup', Signup),
                               (r'/blog/welcome', WelcomePage)
                               ], debug = True)
