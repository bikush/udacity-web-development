import webapp2
import handler

from blog import NewPost, MainPage, SinglePost

URL_BASE = "/assignment-3/blog"
URL_MAIN = URL_BASE + "/?"
URL_SINGLE_POST = URL_BASE + "/(\d+)"
URL_NEWPOST = "/assignment-3/blog/newpost"

config = {
    'jinja_env' : handler.setup_jinja('assignment-3'),
    'url_base' : URL_BASE,
    'url_newpost' : URL_NEWPOST
    }

app = webapp2.WSGIApplication([
    (URL_NEWPOST, NewPost),
    (URL_SINGLE_POST, SinglePost),
    (URL_MAIN, MainPage)
], config=config, debug=True)