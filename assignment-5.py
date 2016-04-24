import webapp2
import handler
import signup
import users

from blogentry import BlogEntry

from google.appengine.ext import db

URL_BASE = "/assignment-5/blog"
URL_MAIN = URL_BASE + "/?"
URL_SINGLE_POST = URL_BASE + "/(\d+)"
URL_NEWPOST = "/assignment-5/blog/newpost"
URL_JSON_SINGLE = URL_SINGLE_POST + "\.json"
URL_JSON_ALL = URL_MAIN + "\.json"
URL_WELCOME = URL_BASE + "/welcome"
URL_LOGOUT = URL_BASE + "/logout"
URL_LOGIN = URL_BASE + "/login"
URL_SIGNUP = URL_BASE + "/signup"


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
            entry = BlogEntry( subject = subject, content = content )
            entry.put()
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

class SinglePost(handler.Handler):
    def get(self, post_id):
        entry = BlogEntry.get_by_id(int(post_id))
        if entry:
            self.render("singlepost.html", 
                subject=entry.subject, 
                content=entry.content, 
                main_url=URL_BASE)
        else:
            self.redirect(URL_BASE)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class MainPage(handler.Handler):
    def get(self):
        entries = BlogEntry.get_last_10()
        self.render("mainpage.html", 
            newpost_url=URL_NEWPOST, 
            single_url=URL_BASE+"/",
            title="My Blog", 
            entries=entries)

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
    'jinja_env' : handler.setup_jinja('assignment-5')
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
    (URL_LOGOUT + "/?", Logout)
], config=config, debug=True)