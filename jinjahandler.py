import webapp2
import jinja2
import os


def setup_jinja(folder_name):
    template_dir = os.path.join(os.path.dirname(__file__), folder_name)
    return jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        jinja_env = self.app.config.get("jinja_env")
        if jinja_env:
            t = jinja_env.get_template(template)
            return t.render(params)
    def render(self, template, **kw): 
        self.write(self.render_str(template, **kw))