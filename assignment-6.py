import webapp2
import handler
import signup
import users
import time

from blogentry import BlogEntry

from google.appengine.ext import db
from google.appengine.api import memcache

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

class TokenSignup(signup.Signup):
    def is_existing_username(self, username):
        existing_user = db.GqlQuery("select * from User where username='"+username+"'").count()
        return existing_user > 0

    def handle_valid_user(self, username, password, email):
        new_user = users.User.create_user(username, password, email)
        new_user.put()

        self.set_secure_cookie('user', username)
        self.redirect( URL_WELCOME )

    def get(self):
        username = self.read_cookie('user')
        if username:
            self.redirect( URL_WELCOME )
        else:
            super(TokenSignup, self).get()

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class TokenWelcome(handler.Handler):
    def get(self):
        username = self.read_cookie('user')
        if username:
            self.render("signupOK.html", username=username)
        else:
            self.redirect( URL_LOGOUT )

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class Login(handler.Handler):
    def generate_login(self, error=""):
        self.render("login.html", error=error)

    def get(self):
        self.generate_login()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        user = users.User.find_and_check_user( username, password )

        if user:
            self.set_secure_cookie('user', username)
            self.redirect( URL_WELCOME )
        else:
            self.generate_login("Invalid login.")

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class Logout(webapp2.RequestHandler):
    def get(self):
        self.response.delete_cookie('user')
        self.redirect( URL_SIGNUP )

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

LAST_10_KEY = 'last10'
LAST_10_TIME_KEY = 'last10_time'

def get_last_10_posts():
    posts = memcache.get( LAST_10_KEY )
    posts_time = memcache.get( LAST_10_TIME_KEY )
    if posts == None or posts_time == None:
        posts = BlogEntry.get_last_10()
        posts_time = time.time()
        memcache.set(LAST_10_KEY, posts)
        memcache.set(LAST_10_TIME_KEY, posts_time)
    return posts, posts_time

def build_post_cache_keys( post_id ):
    cache_key = 'post'+str(post_id)
    return (cache_key,cache_key + '_time')

def get_post_by_id(post_id):
    cache_key, cache_key_time = build_post_cache_keys(post_id)
    post = memcache.get(cache_key)
    post_time = memcache.get(cache_key_time)
    if post == None or post_time == None:
        post = BlogEntry.get_by_id(int(post_id))
        post_time = time.time()
        memcache.set(cache_key, post)
        memcache.set(cache_key_time, post_time)
    return post, post_time

def create_post(subject, content):
    entry = BlogEntry( subject = subject, content = content )
    entry.put()
    
    cache_key, cache_key_time = build_post_cache_keys( str(entry.key().id()) )
    memcache.set(cache_key, entry)
    memcache.set(cache_key_time, time.time())

    posts = memcache.get( LAST_10_KEY )
    if posts:
        posts = [entry] + posts[:-1]
        memcache.set( LAST_10_KEY, posts )
        memcache.set( LAST_10_TIME_KEY, time.time() )

    return entry

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

class NewPost(handler.Handler):
    def generate_newpost_page(self, subject, subject_error, content, content_error):
        self.render("newpost.html", 
            main_url=URL_BASE, subject=subject, 
            subject_error=subject_error, content=content, content_error=content_error)

    def get(self):
        self.generate_newpost_page("", "", "", "")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        verify_subject = len(subject) > 0
        verify_content = len(content) > 0
        if verify_content and verify_subject:
            entry = create_post(subject,content)
            self.redirect(URL_BASE + "/" + str(entry.key().id()))
        else:
            self.generate_newpost_page( 
                subject, 
                "" if verify_subject else "Missing subject.", 
                content, 
                "" if verify_content else "Missing content.")

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

def build_cache_time_str( cache_time ):
    return "Queried %.2f seconds ago" % (time.time() - cache_time)

class SinglePost(handler.Handler):
    def get(self, post_id):
        post, post_time = get_post_by_id(int(post_id))
        if post:
            self.render("singlepost.html", 
                subject=post.subject, 
                content=post.content, 
                main_url=URL_BASE,
                cache_time=build_cache_time_str(post_time)
                )
        else:
            self.redirect(URL_BASE)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class MainPage(handler.Handler):
    def get(self):
        entries, cache_time = get_last_10_posts()
        self.render("mainpage.html", 
            newpost_url=URL_NEWPOST, 
            single_url=URL_BASE+"/",
            title="My Blog", 
            entries=entries,
            cache_time=build_cache_time_str(cache_time) )

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
            self.redirect(URL_MAIN)

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
            self.redirect(URL_MAIN)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

config = {
    'jinja_env' : handler.setup_jinja('assignment-6')
    }

app = webapp2.WSGIApplication([
    (URL_NEWPOST, NewPost),
    (URL_SINGLE_POST, SinglePost),
    (URL_MAIN, MainPage),
    (URL_JSON_SINGLE, JsonBlogSingleAPI),
    (URL_JSON_ALL, JsonBlogAllAPI),
    (URL_SIGNUP + "/?", TokenSignup),
    (URL_WELCOME + "/?", TokenWelcome),
    (URL_LOGIN + "/?", Login),
    (URL_LOGOUT + "/?", Logout),
    (URL_FLUSH + "/?", Flusher)
], config=config, debug=True)