import webapp2
import string
import re
import codecs


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"[\S]+@[\S]+.[\S]+$")


class Signup(webapp2.RequestHandler):
    def generate_signup(self, template_values):
        page_HTML_File = open("assignment-2/signup.html")
        page_HTML = page_HTML_File.read().format(**template_values)
        self.response.write(page_HTML)

    def get(self):
        self.generate_signup({
            "username" : "",
            "username_error" : "",
            "pw_error" : "",
            "verify_pw_error" : "",
            "email" : "",
            "email_error" : ""
            })

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify_password = self.request.get("verify");
        email = self.request.get("email")

        valid_username = USER_RE.match(username)
        valid_password = PASS_RE.match(password)
        valid_verify = password == verify_password
        valid_email = (email == "") or EMAIL_RE.match(email)

        if valid_username and valid_password and valid_verify and valid_email:
            self.redirect("/assignment-2/welcome?username="+username)
        else:
            self.generate_signup({
                "username" : username if valid_username else "",
                "username_error" : "" if valid_username else "That's not a valid username.",
                "pw_error" : "" if valid_password else "That's not a valid password.",
                "verify_pw_error" : "" if not valid_password or valid_verify else "Your passwords didn't match.",
                "email" : email if valid_email else "",
                "email_error" : "" if valid_email else "That's not a valid email."
                })


class Welcome(webapp2.RequestHandler):
    def get(self):
        page_HTML_File = open("assignment-2/signupOK.html")
        page_HTML = page_HTML_File.read().format(self.request.get("username"))
        self.response.write(page_HTML)


class Rot13Page(webapp2.RequestHandler):
    def generate_response_HTML(self,text_string):
        page_HTML_File = open("assignment-2/rot13.html")
        page_HTML = page_HTML_File.read().format(text_string)
        self.response.write(page_HTML)

    def get(self):
        self.generate_response_HTML("")

    def post(self):
        self.generate_response_HTML(codecs.encode(self.request.get("text"), 'rot_13'))



app = webapp2.WSGIApplication([
    ('/assignment-2/signup', Signup),
    ('/assignment-2/welcome', Welcome),
    ('/assignment-2/rot13', Rot13Page)
], debug=True)
