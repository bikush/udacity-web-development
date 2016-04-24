import webapp2
import handler

from blogentry import BlogEntry
from loginout import Login, Logout, TokenSignup, TokenWelcome

from google.appengine.api import memcache
from blog import NewPost, CachedMainPage, CachedSinglePost

URL_BASE = "/assignment-6/blog"
URL_MAIN = URL_BASE + "/?"
URL_SINGLE_POST = URL_BASE + "/(\d+)"
URL_NEWPOST = "/assignment-6/blog/newpost"
URL_JSON_SINGLE = URL_SINGLE_POST + "\.json"
URL_JSON_ALL = URL_MAIN + "\.json"
URL_WELCOME = URL_BASE + "/welcome"
URL_LOGOUT = URL_BASE + "/logout"
URL_LOGIN = URL_BASE + "/login"
URL_SIGNUP = URL_BASE + "/signup"
URL_FLUSH = URL_BASE + "/flush"


########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class Flusher(handler.Handler):
    def get(self):
        memcache.flush_all()
        self.redirect(URL_BASE)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class JsonBlogSingleAPI(webapp2.RequestHandler):
    def get(self, post_id):
        entry = BlogEntry.get_by_id(int(post_id))
        if entry:
            self.response.headers.add_header("Content-Type", "application/json")
            self.response.out.write(entry.to_json())
        else:
            self.redirect(URL_BASE)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class JsonBlogAllAPI(webapp2.RequestHandler):
    def get(self):
        entries = BlogEntry.get_last_10_json()
        if entries:
            self.response.headers.add_header("Content-Type", "application/json")
            self.response.out.write(entries)
        else:
            self.redirect(URL_BASE)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

config = {
    'jinja_env' : handler.setup_jinja('assignment-6'),
    'url_signup' : URL_SIGNUP,
    'url_welcome' : URL_WELCOME,
    'url_logout' : URL_LOGOUT,
    'url_base' : URL_BASE,
    'url_newpost' : URL_NEWPOST
    }

app = webapp2.WSGIApplication([
    (URL_NEWPOST, NewPost),
    (URL_SINGLE_POST, CachedSinglePost),
    (URL_MAIN, CachedMainPage),
    (URL_JSON_SINGLE, JsonBlogSingleAPI),
    (URL_JSON_ALL, JsonBlogAllAPI),
    (URL_SIGNUP + "/?", TokenSignup),
    (URL_WELCOME + "/?", TokenWelcome),
    (URL_LOGIN + "/?", Login),
    (URL_LOGOUT + "/?", Logout),
    (URL_FLUSH + "/?", Flusher)
], config=config, debug=True)