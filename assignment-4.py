import webapp2
import jinjahandler
import signup
import hmac
import users
import random
import string
import hashlib
from google.appengine.ext import db


def hmac_digest( value, key='aX492Di3' ):
    return str(hmac.new(key, value).hexdigest())

def hmac_compare( first, second ):
    return hmac.compare_digest( str(first), str(second) )

def generate_salt():
    return ''.join(random.choice(string.letters + string.digits) for _ in range(10))

def salty_password( password, salt=None ):
    if not salt:
        salt = generate_salt()
    return (str(hashlib.sha256(password+salt).hexdigest()), str(salt))


class TokenSignup(signup.Signup):
    def is_existing_username(self, username):
        existing_user = db.GqlQuery("select * from User where username='"+username+"'").count()
        return existing_user > 0

    def handle_valid_user(self, username, password, email):
        salty_pw = salty_password(password)
        new_user = users.User( 
            username=username, 
            password=salty_pw[0], salt=salty_pw[1], 
            email=None if len(email) == 0 else email )
        new_user.put()

        username_hmac = hmac_digest(username)
        user_cookie = str('user=%s|%s; Path=/' % (username, username_hmac))
        self.response.headers.add_header('Set-Cookie', user_cookie)
        self.redirect('/assignment-4/welcome')

    def get(self):
        username_hash_combo = self.request.cookies.get('user')
        success = False
        if username_hash_combo:
            parts = username_hash_combo.split('|')
            username = parts[0]
            username_hmac = parts[1]
            if hmac_compare(username_hmac, hmac_digest(username)):
                self.redirect('/assignment-4/welcome')
                success = True
        if not success:
            super(TokenSignup, self).get()




class TokenWelcome(jinjahandler.Handler):
    def get(self):
        username_hash_combo = self.request.cookies.get('user')
        success = False
        if username_hash_combo:
            parts = username_hash_combo.split('|')
            username = parts[0]
            username_hmac = parts[1]
            if hmac_compare(username_hmac, hmac_digest(username)):
                self.render("signupOK.html", username=username)
                success = True
        
        if not success:
            self.response.delete_cookie('user')
            self.redirect('/assignment-4/signup')


config = {
    'assignment': 4,
    'jinja_env' : jinjahandler.setup_jinja('assignment-4')
    }

app = webapp2.WSGIApplication([
    ('/assignment-4/signup', TokenSignup),
    ('/assignment-4/welcome', TokenWelcome)
], config=config, debug=True)