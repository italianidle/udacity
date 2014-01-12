import webapp2

from google.appengine.ext import db
from common import Handler

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC ")

        self.render("blog/front.html", posts=posts)

    def get(self):
        self.render_front()

class NewPost(Handler):
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

class Permalink(Handler):
    def render_page(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render("blog/front.html", posts=[post])

    def get(self, post_id):
        self.render_page(post_id)


app = webapp2.WSGIApplication([(r'/blog/?', MainPage),
                               (r'/blog/newpost', NewPost),
                               (r'/blog/(\d+)', Permalink)
                               ], debug = True)
