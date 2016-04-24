import webapp2
import jinja2
import os

from blogentry import BlogEntry

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'assignment-3')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

URL_BASE = "/assignment-3/blog"
URL_MAIN = URL_BASE + "/?"
URL_SINGLE_POST = URL_BASE + "/(\d+)"
URL_NEWPOST = "/assignment-3/blog/newpost"

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw): 
        self.write(self.render_str(template, **kw))

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class NewPost(Handler):
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

class SinglePost(Handler):
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

class MainPage(Handler):
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

app = webapp2.WSGIApplication([
    (URL_NEWPOST, NewPost),
    (URL_SINGLE_POST, SinglePost),
    (URL_MAIN, MainPage)
], debug=True)