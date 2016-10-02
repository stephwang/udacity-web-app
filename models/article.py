from google.appengine.ext import db

class Article(db.Model):
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    
    def render(self):
        p = self.content.replace('\n', '<br>')
        return p