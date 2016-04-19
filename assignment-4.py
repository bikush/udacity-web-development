import webapp2
import jinjahandler
import signup


class TokenSignup(signup.Signup):
    def handle_valid_user(self, username, password, email):
        self.response.headers.add_header('Set-Cookie', str('user=%s; Path=/' % username))
        self.redirect('/assignment-4/welcome')


class TokenWelcome(jinjahandler.Handler):
    def get(self):
        username = self.request.cookies.get('user')
        if username:
            self.render("signupOK.html", username=username)
        else:
            self.redirect('/assignment-4/signup')


config = {
    'assignment': 4,
    'jinja_env' : jinjahandler.setup_jinja('assignment-4')
    }

app = webapp2.WSGIApplication([
    ('/assignment-4/signup', TokenSignup),
    ('/assignment-4/welcome', TokenWelcome)
], config=config, debug=True)