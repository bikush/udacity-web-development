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
URL_HISTORY = URL_BASE + "/_history"
PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)?'

def extract(string_item, count):
    if count < len(string_item):
        return string_item[:count] + "..."
    return string_item


class WikiEntry(db.Model):
    path = db.StringProperty( required = True )
    content = db.TextProperty( required = True )
    created = db.DateTimeProperty( auto_now_add = True )

    def create_history_entry(self):
        version_str = self.path + "?v=" + str( self.key().id() )
        return { 'date' : self.created,
                 'summary' : extract(self.content, 77),
                 'content' : self.content,
                 'view_url' : URL_BASE + version_str,
                 'edit_url' : URL_EDIT + version_str }

    @classmethod
    def get_entry(cls, path, version=None):
        #TODO: memcache this
        if version:
            return WikiEntry.get_by_id(int(version))

        wiki = memcache.get(path)
        if wiki == None:
            wiki = cls.all().filter("path =", path).order("-created").get()
            if wiki:
                memcache.set(path, wiki)
        return wiki

    @classmethod
    def get_history(cls, path, update = True):
        key = "_history" + path
        history = memcache.get(key)
        if history == None and update:
            items = cls.all().filter("path =", path).order("-created")
            history = []
            for item in items:
                history.append( item.create_history_entry() )
            memcache.set(key, history)
        return history

    @classmethod
    def create_entry(cls, path, content):
        entry = WikiEntry( path = path, content = content   )
        entry.put()
        memcache.set(path, entry)

        key = "_history" + path
        history = memcache.get(key)
        if history != None:
            history = [entry.create_history_entry()] + history
            memcache.set(key, history)

        return entry


class WikiRead(handler.Handler):
    def get(self, *args):
        username = self.read_cookie('user')

        path = '/' if args == None or args[0] == None else args[0]
        version = self.request.get("v")
        entry = WikiEntry.get_entry(path, version)

        if not entry and username:
            if version:
                self.redirect(URL_BASE + path)
            else:
                self.redirect(URL_EDIT + path)
        else:
            content = '' if not entry else entry.content
            wiki_config = {
                'edit_link' : URL_EDIT + str(path) + ('' if not version else ("?v="+version)),
                'history_link' : URL_HISTORY + str(path),
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
        version = self.request.get("v")        
        entry = WikiEntry.get_entry(path, version)

        if not entry and version:
            self.redirect(URL_BASE+path)
            return

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


class WikiHistory(handler.Handler):
    def get(self, *args):
        username = self.read_cookie('user')
        path = '/' if args == None or args[0] == None else args[0]
        history = WikiEntry.get_history(path)
        history_config = {
            'entries' : history,
            'edit_link' : URL_EDIT + str(path),
            'view_link' :  URL_BASE + str(path),
            'logout_link' : URL_LOGOUT,
            'login_link' : URL_LOGIN,
            'signup_link' : URL_SIGNUP,
            'username' : username
        }
        self.render("wiki_history.html", **history_config)


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
    (URL_HISTORY + PAGE_RE, WikiHistory),
    (URL_BASE + PAGE_RE, WikiRead)
], config=config, debug=True)