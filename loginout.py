import webapp2
import handler
import signup
import users

from google.appengine.ext import db

# Required in app config dictionary:
# url_login_success - redirect on successful login
# url_logout - wisit this link to logout
# url_logout_redirect - redirect page upon logout


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
        self.redirect( self.app.config.get('url_login_success') )

    def get(self):
        username = self.read_cookie('user')
        if username:
            self.redirect( self.app.config.get('url_login_success') )
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
            self.redirect( self.app.config.get('url_logout') )

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
            self.redirect( self.app.config.get('url_login_success') )
        else:
            self.generate_login("Invalid login.")

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class Logout(webapp2.RequestHandler):
    def get(self):
        self.response.delete_cookie('user')
        self.redirect( self.app.config.get('url_logout_redirect') )

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################
