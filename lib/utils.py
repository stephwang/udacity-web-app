import re
import hmac
import random
import string
import hashlib
import time
import lib.constants as c

import logging

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(c.SECRET, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

# validation checks for signup form
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

# storing user information 
def make_pw_hash(username, password, salt=""):
    if not salt:
        salt = ''.join(random.choice(string.letters) for x in xrange(5))
    h = hashlib.sha256(username + password + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(username, password, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(username, password, salt)