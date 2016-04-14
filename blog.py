import webapp2
import jinja2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'assignment-3')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

URL_MAIN = "/assignment-3/blog"
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
    def generate_newpost_page(self):
        self.render("newpost.html", main_url=URL_MAIN)

    def get(self):
        self.generate_newpost_page()

    def post(self):
        self.redirect(URL_MAIN)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

class MainPage(Handler):
    def get(self):
        self.response.write("Main page. <a href=\""+URL_NEWPOST+"\">New post</a>")

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

app = webapp2.WSGIApplication([
    (URL_NEWPOST, NewPost),
    (URL_MAIN, MainPage)
], debug=True)