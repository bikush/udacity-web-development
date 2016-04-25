import webapp2
import handler
import logging

from loginout import Login, Logout, TokenSignup, TokenWelcome

from google.appengine.ext import db
from google.appengine.api import memcache

URL_BASE = "/assignment-final/wiki"
URL_LOGOUT = URL_BASE + "/logout"
URL_LOGIN = URL_BASE + "/login"
URL_SIGNUP = URL_BASE + "/signup"
URL_EDIT = URL_BASE + "/_edit"
PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)?'


class WikiEntry(db.Model):
    path = db.StringProperty( required = True )
    content = db.TextProperty( required = True )
    created = db.DateTimeProperty( auto_now_add = True )

    @classmethod
    def get_latest_entry(cls, path):
        wiki = memcache.get(path)
        if wiki == None:
            wiki = cls.all().filter("path =", path).order("-created").get()
            if wiki:
                memcache.set(path, wiki)
        return wiki

    @classmethod
    def create_entry(cls, path, content):
        entry = WikiEntry( path = path, content = content   )
        entry.put()
        memcache.set(path, entry)
        return entry

class WikiRead(handler.Handler):
    def get(self, *args):
        username = self.read_cookie('user')

        path = '/' if args == None or args[0] == None else args[0]
        entry = WikiEntry.get_latest_entry(path)
        if not entry and username:
            self.redirect(URL_EDIT + path)
        else:
            content = '' if not entry else entry.content
            wiki_config = {
                'edit_link' : URL_EDIT + str(path),
                'history_link' : 'history',
                'logout_link' : URL_LOGOUT,
                'login_link' : URL_LOGIN,
                'signup_link' : URL_SIGNUP,
                'username' : username,
                'content' : content
            }
            self.render("wiki_read.html", **wiki_config)


class WikiEdit(handler.Handler):
    def get(self, *args):
        username = self.read_cookie('user')
        if not username:
            self.redirect(URL_BASE)
            return
        
        path = '/' if args == None or args[0] == None else args[0]
        entry = WikiEntry.get_latest_entry(path)
        content = '' if not entry else entry.content

        edit_config = {
                'main_link' : URL_BASE + str(path) if entry else URL_BASE,
                'logout_link' : URL_LOGOUT,
                'path' : path,
                'username' : username,
                'content' : content
            }
        self.render("wiki_edit.html", **edit_config)

    def post(self, *args):
        username = self.read_cookie('user')
        if not username:
            self.redirect(URL_BASE)
            return

        path = '/' if args == None or args[0] == None else args[0]
        content = self.request.get("content")
        WikiEntry.create_entry( path, content )

        self.redirect(URL_BASE + path)


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
    (URL_EDIT + PAGE_RE, WikiEdit),
    (URL_BASE + PAGE_RE, WikiRead)
], config=config, debug=True)