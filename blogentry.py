import json
import time

from google.appengine.ext import db
from google.appengine.api import memcache

LAST_10_KEY = 'last10'
LAST_10_TIME_KEY = 'last10_time'

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


    @classmethod
    def get_last_10_posts(cls):
        posts = memcache.get( LAST_10_KEY )
        posts_time = memcache.get( LAST_10_TIME_KEY )
        if posts == None or posts_time == None:
            posts = cls.get_last_10()
            posts_time = time.time()
            memcache.set(LAST_10_KEY, posts)
            memcache.set(LAST_10_TIME_KEY, posts_time)
        return posts, posts_time

    @classmethod
    def build_post_cache_keys( cls, post_id ):
        cache_key = 'post'+str(post_id)
        return (cache_key,cache_key + '_time')

    @classmethod
    def get_post_by_id(cls, post_id):
        cache_key, cache_key_time = cls.build_post_cache_keys(post_id)
        post = memcache.get(cache_key)
        post_time = memcache.get(cache_key_time)
        if post == None or post_time == None:
            post = cls.get_by_id(int(post_id))
            post_time = time.time()
            memcache.set(cache_key, post)
            memcache.set(cache_key_time, post_time)
        return post, post_time

    @classmethod
    def create_post(cls, subject, content):
        entry = cls( subject = subject, content = content )
        entry.put()
        
        cache_key, cache_key_time = cls.build_post_cache_keys( str(entry.key().id()) )
        memcache.set(cache_key, entry)
        memcache.set(cache_key_time, time.time())

        posts = memcache.get( LAST_10_KEY )
        if posts:
            posts = [entry] + posts[:-1]
            memcache.set( LAST_10_KEY, posts )
            memcache.set( LAST_10_TIME_KEY, time.time() )

        return entry