
import webapp2
import handler
import time

from blogentry import BlogEntry
from loginout import Login, Logout, TokenSignup, TokenWelcome

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class NewPost(handler.Handler):
    def generate_newpost_page(self, subject, subject_error, content, content_error):
        self.render("newpost.html", 
            main_url=self.app.config.get('url_base'), subject=subject, 
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
            self.redirect(self.app.config.get('url_base') + "/" + str(entry.key().id()))
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
                main_url=self.app.config.get('url_base')
                )
        else:
            self.redirect(self.app.config.get('url_base'))

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class MainPage(handler.Handler):
    def get(self):
        entries = BlogEntry.get_last_10()
        self.render("mainpage.html", 
            newpost_url=self.app.config.get('url_newpost'), 
            single_url=self.app.config.get('url_base')+"/",
            title="My Blog", 
            entries=entries)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

def build_cache_time_str( cache_time ):
    return "Queried %.2f seconds ago" % (time.time() - cache_time)

class CachedSinglePost(handler.Handler):
    def get(self, post_id):
        post, post_time = BlogEntry.get_post_by_id(int(post_id))
        if post:
            self.render("singlepost.html", 
                subject=post.subject, 
                content=post.content, 
                main_url=self.app.config.get('url_base'),
                cache_time=build_cache_time_str(post_time)
                )
        else:
            self.redirect(self.app.config.get('url_base'))

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class CachedMainPage(handler.Handler):
    def get(self):
        entries, cache_time = BlogEntry.get_last_10_posts()
        self.render("mainpage.html", 
            newpost_url=self.app.config.get('url_newpost'), 
            single_url=self.app.config.get('url_base')+"/",
            title="My Blog", 
            entries=entries,
            cache_time=build_cache_time_str(cache_time) )

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################
