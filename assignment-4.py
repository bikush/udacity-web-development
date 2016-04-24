import webapp2
import handler

from loginout import Login, Logout, TokenSignup, TokenWelcome

config = {
    'jinja_env' : handler.setup_jinja('assignment-4'),
    'url_signup' : '/assignment-4/signup',
    'url_welcome' : '/assignment-4/welcome',
    'url_logout' : '/assignment-4/logout'
    }

app = webapp2.WSGIApplication([
    ('/assignment-4/signup', TokenSignup),
    ('/assignment-4/welcome', TokenWelcome),
    ('/assignment-4/login', Login),
    ('/assignment-4/logout', Logout)
], config=config, debug=True)