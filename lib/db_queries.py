import logging
import time

from google.appengine.api import memcache
from google.appengine.ext import db

from models.article import Article
from models.user import User
import lib.utils as utils

def get_article_all_versions(title):
    curr_article = memcache.get(title)

    if curr_article is None:
        logging.error("DB QUERY BEING RUN")
        curr_article = db.GqlQuery("SELECT * FROM Article " 
                                    "WHERE path= :1" 
                                    " ORDER BY created asc", title)
        curr_article = list(curr_article)
        
        # not in db
        if not curr_article:
            memcache.set(title, [])
        # found in db
        else:
            memcache.set(title, curr_article)

    return curr_article

def get_article(title, version=None):
    curr_article = get_article_all_versions(title)
    
    if curr_article:
        # no version means requesting latest version
        if not version:
            return curr_article[(len(curr_article) - 1)]
        else:
            index = int(version) - 1
            return curr_article[index]

def post_article(title, content):
    logging.error("DB QUERY BEING RUN")
    
    b = Article(path=title, content=content)
    key = b.put()
    
    # update memcache
    m = memcache.get(title)
    m.append(b)
    memcache.set(title, m)
        
    return b
    
def get_user(username, update=False):
    logging.error("DB QUERY BEING RUN")
    curr_user = db.GqlQuery("SELECT * FROM User WHERE username='" + username + "'")
    
    return curr_user.get()

def create_user(username, pw_hash, email):
    # create new user
    u = User(username=username, pw_hash=pw_hash, email=email)
    u.put()
    
    return u

def attempt_login(username, password):
    logging.error("DB QUERY BEING RUN")
    u = get_user(username)
    if u and utils.valid_pw(username, password, u.pw_hash):
        return u