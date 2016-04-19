import re
from google.appengine.ext import db

EMAIL_RE = re.compile(r"[\S]+@[\S]+.[\S]+$")

def validate_email( email ):
    if email and len(email) > 0:
        EMAIL_RE.match(email)
    return True

class User(db.Model):
    username = db.StringProperty( required = True )
    password = db.StringProperty( required = True )
    salt = db.StringProperty( required = True )
    email = db.EmailProperty( validator=validate_email )
    created = db.DateTimeProperty( auto_now_add = True )