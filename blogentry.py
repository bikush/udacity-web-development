import json

from google.appengine.ext import db

class BlogEntry(db.Model):
    subject = db.StringProperty( required = True )
    content = db.TextProperty( required = True )
    created = db.DateTimeProperty( auto_now_add = True )
    modified = db.DateTimeProperty( auto_now_add = True )

    def to_object(self):
        return { "subject" : self.subject,
                 "content" : self.content,
                 "created" : self.created.strftime("%c"),
                 "last_modified" : self.modified.strftime("%c") }

    def to_json(self):
        return json.dumps( self.to_object() )

    @classmethod
    def get_last_10(cls):
        return db.GqlQuery("select * from BlogEntry order by created desc").fetch(10)

    @classmethod
    def get_last_10_json(cls):
        entries = cls.get_last_10()
        all_items = [ enrty.to_object() for enrty in entries ]
        return json.dumps(all_items)