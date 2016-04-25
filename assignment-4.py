import webapp2
import handler

from loginout import Login, Logout, TokenSignup, TokenWelcome

config = {
    'jinja_env' : handler.setup_jinja('assignment-4'),
    'url_login_success' : '/assignment-4/welcome',
    'url_logout' : '/assignment-4/logout',
    'url_logout_redirect' : '/assignment-4/signup'
    }

app = webapp2.WSGIApplication([
    ('/assignment-4/signup', TokenSignup),
    ('/assignment-4/welcome', TokenWelcome),
    ('/assignment-4/login', Login),
    ('/assignment-4/logout', Logout)
], config=config, debug=True)