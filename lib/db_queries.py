import logging

from google.appengine.api import memcache
from google.appengine.ext import db

from models.article import Article
from models.user import User
import lib.utils as utils

def get_article(title, update=False):
    key = title
    curr_article = memcache.get(key)
    
    if curr_article is None or update == True:
        logging.error("DB QUERY BEING RUN")
        curr_article = Article.get_by_key_name(key_names=title)
        if curr_article is None:
            memcache.set(key, '')
        else:
            memcache.set(key, curr_article)

    return curr_article
    

def post_article(title, content):
    logging.error("DB QUERY BEING RUN")
    
    b = Article.get_or_insert(key_name=title)
    b.content = content
    b.put()
    get_article(title, True)
        
    return True
    
def get_user(username, update=False):
    logging.error("DB QUERY BEING RUN")
    curr_user = db.GqlQuery("SELECT * FROM User WHERE username='" + username + "'")
    
    return curr_user

def create_user(username, pw_hash, email):
    # create new user
    u = User(username=username, pw_hash=pw_hash, email=email)
    u.put()
    
    return u

def attempt_login(username, password):
    logging.error("DB QUERY BEING RUN")
    u = get_user(username).get()
    if u and utils.valid_pw(username, password, u.pw_hash):
        return u