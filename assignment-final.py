import webapp2
import handler
import logging

from loginout import Login, Logout, TokenSignup, TokenWelcome

from google.appengine.ext import db

URL_BASE = "/assignment-final/wiki"
URL_LOGOUT = URL_BASE + "/logout"
URL_LOGIN = URL_BASE + "/login"
URL_SIGNUP = URL_BASE + "/signup"
PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)?'


class WikiEntry(db.Model):
    path = db.StringProperty( required = True )
    content = db.TextProperty( required = True )
    created = db.DateTimeProperty( auto_now_add = True )

    @classmethod
    def get_latest_entry(cls, path):
        return cls.all().filter("path =", path).order("-created").get()

class WikiRead(handler.Handler):
    def get(self, *args):
        path = '/' if args == None or args[0] == None else args[0]

        entry = WikiEntry.get_latest_entry(path)
        content = ''
        if not entry:
            content = '<h2>NO CONTENT</h2><br>' + str(path)
        else:
            content = entry.content

        username = self.read_cookie('user')
        wiki_config = {
            'edit_link' : 'edit',
            'history_link' : 'history',
            'logout_link' : URL_LOGOUT,
            'login_link' : URL_LOGIN,
            'signup_link' : URL_SIGNUP,
            'username' : username,
            'content' : content
        }
        self.render("wiki_read.html", **wiki_config)



config = {
    'jinja_env' : handler.setup_jinja('assignment-final'),
    'url_login_success' : URL_BASE,
    'url_logout' : URL_LOGOUT,
    'url_logout_redirect' : URL_BASE
    }

app = webapp2.WSGIApplication([
    (URL_SIGNUP + "/?", TokenSignup),
    (URL_LOGIN + "/?", Login),
    (URL_LOGOUT + "/?", Logout),
    (URL_BASE + PAGE_RE, WikiRead)
], config=config, debug=True)