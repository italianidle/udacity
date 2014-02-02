from google.appengine.ext import db
from utils import make_pw_hash, valid_pw

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, user_id):
        return User.get_by_id(user_id, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def as_dict(self):
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.ctime(),
             'last_modified': self.last_modified.ctime()}
        return d
    
    @classmethod
    def by_id(cls, post_id):
        return Post.get_by_id(post_id, parent = blog_key())

    @classmethod
    def new(cls, subject, content):
        return Post(parent = blog_key(), subject = subject, content = content)

def arts_key(name = 'default'):
    return db.Key.from_path('arts', name)

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    coords = db.GeoPtProperty()

    @classmethod
    def top(cls, limit = 10):
        return db.GqlQuery("SELECT * FROM Art "
                           "WHERE ANCESTOR IS :1 "
                           "ORDER BY created DESC "
                           "LIMIT 10",
                           arts_key())

    @classmethod
    def new(cls, title, art):
        return Art(parent=arts_key(), title = title, art = art)

def page_key(path):
    return db.Key.from_path('/root' + path, 'pages')

class Page(db.Model):
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @classmethod
    def by_path(cls, path):
        p = Page.all().ancestor(page_key(path)).get()
        return p

    @classmethod
    def new(cls, path, content=''):
        return Page(parent=page_key(path), content=content)
