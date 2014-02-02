import webapp2
import os
import jinja2
import json

from utils import *
from models import User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, data):
        s = json.dumps(data)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.write(s)

    def set_secure_cookie(self, name, value):
        cookie_val = ''
        if value:
            cookie_val = make_secure_val(value)
        self.response.headers.add_header('Set-Cookie', 
                                         '%s=%s;Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        secure_cookie = self.request.cookies.get(name)
        return secure_cookie and check_secure_val(secure_cookie)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.set_secure_cookie('user_id', '')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id = self.read_secure_cookie('user_id')
        self.user = user_id and User.by_id(int(user_id))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'
        
class Signup(BaseHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['username_error'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['password_error'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['verify_error'] = "Your passwords didn't match."
            have_error = True
        
        if self.email and not valid_email(self.email):
            params['email_error'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render("signup-form.html", **params)
        else:
            user = User.by_name(self.username)
            if user:
                username_error = "That user already exists."
                self.render("signup-form.html", username_error = username_error)
            else:
                self.done()

    def done(self):
        raise NotImplementedError

