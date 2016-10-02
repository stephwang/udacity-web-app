import webapp2

import handlers.wiki as wiki

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([
    ('/signup', wiki.SignupHandler), 
    ('/login', wiki.LoginHandler),
    ('/logout', wiki.LogoutHandler),
    ('/_edit' + PAGE_RE, wiki.EditPageHandler),
    ('/_history' + PAGE_RE, wiki.HistoryPageHandler),
    (PAGE_RE, wiki.WikiPageHandler)
], debug=True)