import webapp2
import re
import cgi

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PWD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_username(username):
    return USER_RE.match(username)

def valid_password(password):
    return PWD_RE.match(password)

def valid_email(email):
    return EMAIL_RE.match(email)


signup_html="""
<html>
  <head>
    <title>Signup</title>
    <style>
      form div {
        margin: 5px;
      }
      label {
        display: inline-block;
        width: 120px; 
        text-align:right;
      }
      
      .error {
        color: red;
      }
    </style>
  </head>
  <body>
    <h2>Signup</h2>
    <form method="post">
     <div>
       <label for="username">Username</label>
       <input type="text" name="username" value="%(username)s">
       <span class="error">%(username_error)s</span>
     </div>
     <div>
       <label for="password">Password</label>
       <input type="password" name="password" value="">
       <span class="error">%(password_error)s</span>
     </div>
     <div>
       <label for="verify">Verify Password</label>
       <input type="password" name="verify" value="">
       <span class="error">%(verify_error)s</span>
     </div>
     <div>
       <label for="email">Email (optional)</label>
       <input type="text" name="email" value="%(email)s">
       <span class="error">%(email_error)s</span>
     </div> 
    <input type="submit">
    </form>
  </body>
</html>
"""

welcome_html="""
<html>
  <head>
    <title>Welcome</title>
  </head>
  <body>
    <h2>Welcome, %(username)s!</h2>
  </body>
</html>
"""


class SignupHandler(webapp2.RequestHandler):
    def write_html(self, username="", email="", username_error="", password_error="", verify_error="", email_error=""):
        self.response.out.write(signup_html % {"username": cgi.escape(username, quote = True),
                                               "email": cgi.escape(email, quote = True),
                                               "username_error": cgi.escape(username_error, quote = True),
                                               "password_error": cgi.escape(password_error, quote = True),
                                               "verify_error": cgi.escape(verify_error, quote = True),
                                               "email_error": cgi.escape(email_error, quote = True)})

    def get(self):
       self.write_html()

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
            self.write_html(username, email, username_error, password_error, verify_error, email_error)
        else:
            self.redirect("/unit2/welcome?username=" + username)


class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.get("username")
        if username:
            self.response.out.write(welcome_html % {"username": username})
        else:
            self.redirect("/unit2/signup")


app = webapp2.WSGIApplication([('/unit2/signup', SignupHandler),
                               ('/unit2/welcome', WelcomeHandler)], debug = True)
