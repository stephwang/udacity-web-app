import webapp2
import jinja2
import os
import re

import random
import string
import hashlib
import hmac

import models.posts as posts
import models.users as users

from google.appengine.ext import db

SECRET = 'supersecret'

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)        
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPageHandler(Handler):
    def get(self):
        u = db.GqlQuery("select * from User")
        for user in u:
            user.delete()
        self.response.out.write('hello!')

class SignupHandler(Handler):
    def get(self):
        self.render('signup.html')
        
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        password2 = self.request.get('verify')
        email = self.request.get('email')
        errors = 0
        
        params = dict(username = username, email = email)
        
        # form input validation
        if not valid_username(username):
            params['username_error'] = "That's not a valid username."
            errors += 1
        if not valid_password(password):
            params['password_error'] = "That's not a valid password."
            errors += 1
        if not password_match(password, password2):
            params['password_match_error'] = "Passwords do not match."
            errors += 1
        if email and not valid_email(email):
            params['email_error'] = "That's not a valid email."
            errors += 1
        
        # check if user exists already
        u = db.GqlQuery("select * from User where username='" + username + "'")
        if u.get():
            params['username_error'] = "User already exists"
            errors += 1
        
        if errors > 0:
            self.render('signup.html', **params)
        else:
            # create new user
            p = make_pw_hash(username, password)
            u = users.User(username=username, pwhash=p, email=email)
            u.put()
            
            # add cookie
            userhash = hash_user(username)
            cookie = "user="+username+"|"+userhash+"; Path=/"
            self.response.headers.add_header('Set-Cookie', str(cookie))
            
            self.redirect('/welcome')

class LoginHandler(Handler):
    def get(self):
        self.render('login.html')
        
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        error = "invalid login"
        errors = 0

        # form input validation
        if not username and not password:
            errors += 1
        else:
            u = db.GqlQuery("select * from User where username='" + username + "'").get()
            if not u:
                errors += 1
            else:
                salt = u.pwhash.split(',')[1]
                if make_pw_hash(username, password, salt) != str(u.pwhash):
                    errors += 1
        
        if errors > 0:
            self.render('login.html', username=username, error=error)
        else:
            # add cookie
            userhash = hash_user(username)
            cookie = "user="+username+"|"+userhash+"; Path=/"
            self.response.headers.add_header('Set-Cookie', str(cookie))
            # redirect to welcome page
            self.redirect('/welcome')

class LogoutHandler(Handler):
    def get(self):
        cookie = "user=; Path=/"
        self.response.headers.add_header('Set-Cookie', str(cookie))
        self.redirect('/signup')

class WelcomeHandler(Handler):
    def get(self):
        u = self.request.cookies.get('user')
        
        if not u or u=='':
            self.redirect('/signup')
        else:
            username, uhash = u.split('|')
            if hash_user(username) == uhash:
                self.render("welcome.html", username = username)
            else:
                self.redirect('/signup')

class BlogHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * from Blogpost ORDER BY created desc LIMIT 10")
        self.render("blog.html", posts=posts)

class PostPageHandler(BlogHandler):
    def get(self, post_id):
        post = posts.Blogpost.get_by_id(int(post_id))
        
        if not post:
            self.error(404)
            return
        
        self.render("permalink.html", post=post)

class NewPostHandler(Handler):
    def get(self):
        self.render("newpost.html")
    
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            b = posts.Blogpost(title=subject, contents=content)
            b.put()
            
            self.redirect("/blog/%s" % str(b.key().id()))
        else:
            error = "both title and contents are required!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class AsciiHandler(Handler):
    def render_front(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        self.render("ascii.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_front()
    
    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")
        
        if title and art:
            a = posts.Art(title=title, art=art)
            a.put()
            
            self.redirect("/ascii")
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title=title, art=art, error=error)

app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/signup', SignupHandler), 
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/welcome', WelcomeHandler),
    ('/ascii', AsciiHandler),
    ('/blog', BlogHandler),
    ('/blog/([0-9]+)', PostPageHandler),
    ('/blog/newpost', NewPostHandler)
], debug=True)

def valid_username(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return USER_RE.match(username)
    
def valid_password(password):
    PASS_RE = re.compile(r"^.{3,20}$")
    return PASS_RE.match(password)
    
def password_match(password, password2):
    return password == password2

def valid_email(email):
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
    return EMAIL_RE.match(email) 
    
def make_pw_hash(name, password, salt=""):
    if not salt:
        salt = ''.join(random.choice(string.letters) for x in xrange(5))
    h = hashlib.sha256(name + password + salt).hexdigest()
    return '%s,%s' % (h, salt)

def hash_user(username):
    return hmac.new(SECRET, username).hexdigest()