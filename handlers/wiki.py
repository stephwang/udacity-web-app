import json
import time
from google.appengine.api import memcache


from lib import utils
from handlers.general import Handler
from models.user import User
import lib.db_queries as query

import logging

class WikiPageHandler(Handler):
    def get(self, title):
        article = query.get_article(title)
        if article:
            content = article.render()
            self.render('article.html', title=title, content=content)
        else:
            self.redirect('/_edit%s' % title)

class EditPageHandler(Handler):
    def get(self, title, content='', error=''):
        if self.user:
            article = query.get_article(title)
            if article:
                content = article.content
            self.render("edit_article.html", title=title, content=content, error=error)
        else:
            self.redirect('/login')
    
    def post(self, title):
        content = self.request.get('content')
        if content:
            query.post_article(title=title, content=content)
            self.redirect("%s" % title)
        else:
            error = "contents are required!"
            self.render("edit_article.html", title=title, content=content, error=error)


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
        if not utils.valid_username(username):
            params['username_error'] = "That's not a valid username."
            errors += 1
        if not utils.valid_password(password):
            params['password_error'] = "That's not a valid password."
            errors += 1
        if not utils.password_match(password, password2):
            params['password_match_error'] = "Passwords do not match."
            errors += 1
        if email and not utils.valid_email(email):
            params['email_error'] = "That's not a valid email."
            errors += 1
        
        # check if user exists already
        u = query.get_user(username)
        if u.get():
            params['username_error'] = "User already exists"
            errors += 1
        
        if errors > 0:
            self.render('signup.html', **params)
        else:
            pw_hash = utils.make_pw_hash(username, password)
            u = query.create_user(username, pw_hash, email)
            
            # add cookie
            self.login(u)
            
            self.redirect('/')

class LoginHandler(Handler):
    def get(self):
        self.render('login.html')
        
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        error = "invalid login"

        u = query.attempt_login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            self.render('login.html', username=username, error=error)

class LogoutHandler(Handler):
    def get(self):
        self.logout()
        self.redirect('/login')

# class HistoryPageHandler(BlogHandler):
#     def get(self):
#         post_query_key = post_id + '_query_time'
#         post = memcache.get(post_id)
        
#         if not post:
#             post = posts.Blogpost.get_by_id(int(post_id))
#             memcache.set(post_id, post)
#             memcache.set(post_query_key, int(time.time()))
        
#         if not post:
#             self.error(404)
#             return
        
#         if self.request.url.endswith('.json'):
#             p= {'subject': post.title,
#                 'content':post.contents, 
#                 'created': post.created.strftime('%c')
#             }
#             self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
#             self.write(json.dumps(p))
#         else:
#             post_last_queried = int(time.time()-memcache.get(post_query_key))
#             self.render("permalink.html", post=post, post_last_queried=post_last_queried)