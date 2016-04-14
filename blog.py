import webapp2
import jinja2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'assignment-3')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw): 
        self.write(self.render_str(template, **kw))


class NewPost(webapp2.RequestHandler):
    def get(self):
        self.response.write("New post page.")


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Main page. <a href=\"/assignment-3/blog/newpost\">New post</a>")


app = webapp2.WSGIApplication([
    ('/assignment-3/blog/newpost', NewPost),
    ('/assignment-3/blog', MainPage)
], debug=True)