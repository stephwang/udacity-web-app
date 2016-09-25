from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required = True)
    pwhash = db.StringProperty(required = True)
    email = db.StringProperty()
    
    @classmethod
    def by_name(cls, name):
        u = User.all().filter('username =', name).get()
        return u