import re
import random
import string
import hashlib
from google.appengine.ext import db

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

EMAIL_RE = re.compile(r"[\S]+@[\S]+.[\S]+$")

def validate_email( email ):
    if email and len(email) > 0:
        EMAIL_RE.match(email)
    return True

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

def generate_salt():
    return ''.join(random.choice(string.letters + string.digits) for _ in range(10))

def salty_password( password, salt=None ):
    if not salt:
        salt = generate_salt()
    return (str(hashlib.sha256(password+salt).hexdigest()), str(salt))

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class User(db.Model):
    username = db.StringProperty( required = True )
    password = db.StringProperty( required = True )
    salt = db.StringProperty( required = True )
    email = db.EmailProperty( validator=validate_email )
    created = db.DateTimeProperty( auto_now_add = True )

    @classmethod
    def create_user(cls, username, password, email=None):
        salty_pw = salty_password(password)
        email = None if (not email) or (len(email) == 0) else email 
        return cls( 
            username = username, 
            password = salty_pw[0], 
            salt = salty_pw[1], 
            email = email )

    @classmethod
    def find_and_check_user(cls, username, password):
        existing_user = db.GqlQuery("select * from User where username='"+username+"'")
        for user in existing_user:
            salty_pw = salty_password(password,user.salt)
            if str(salty_pw[0]) == str(user.password):
                return user
            break