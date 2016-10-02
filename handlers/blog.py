import webapp2
import jinja2
import os
import re
import models.posts

from google.appengine.ext import db

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

class MainPage(Handler):
    def get(self):
        self.render('signup.html')
        
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        password2 = self.request.get('password2')
        email = self.request.get('email')
        errors = 0
        
        params = dict(username = username, email = email)
        
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
        
        if errors > 0:
            self.render('signup.html', **params)
        else:
            self.redirect('/welcome?username=' + username)

class WelcomeHandler(Handler):
    def get(self):
        params = dict(username = self.request.get('username'))
        self.render("welcome.html", **params)

class BlogHandler(Handler):
    def get(self):
        self.render("blog.html")

class NewPostHandler(Handler):
    def get(self):
        self.render("newpost.html")

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
            a = Art(title=title, art=art)
            a.put()
            
            self.redirect("/ascii")
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title=title, art=art, error=error)

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