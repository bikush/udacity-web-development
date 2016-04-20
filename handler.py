import webapp2
import jinja2
import os
import hmac

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

def setup_jinja(folder_name):
    template_dir = os.path.join(os.path.dirname(__file__), folder_name)
    return jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

def hmac_digest( value, key='aX492Di3' ):
    return str(hmac.new(key, value).hexdigest())

def hmac_compare( first, second ):
    #return hmac.compare_digest( str(first), str(second) )
    return str(first) == str(second)

########################################
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #
########################################

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

    def set_cookie(self, cookie_name, cookie_value):
        cookie = str('%s=%s; Path=/' % (cookie_name, cookie_value))
        self.response.headers.add_header('Set-Cookie', cookie)

    def set_secure_cookie(self, cookie_name, cookie_value):
        self.set_cookie(cookie_name, "%s|%s" % (cookie_value, hmac_digest(cookie_value)))

    def read_cookie(self, cookie_name):
        cookie_value = self.request.cookies.get(cookie_name)
        if cookie_value:
            cookie_parts = cookie_value.split('|')
            if len(cookie_parts) > 1:
                if hmac_compare(cookie_parts[1], hmac_digest(cookie_parts[0])):
                    return cookie_parts[0]
            else:
                return cookie_value
