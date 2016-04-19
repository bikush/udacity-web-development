import string
import re
import jinjahandler


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"[\S]+@[\S]+.[\S]+$")


class Signup(jinjahandler.Handler):
    def generate_signup(self, template_values):
        self.render("signup.html", **template_values)

    def handle_valid_user(self, username, password, email):
        #self.redirect("/assignment-4/welcome?username="+username)
        pass

    def validate_username(self, username):
        return USER_RE.match(username)

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

        valid_username = self.validate_username(username)
        valid_password = PASS_RE.match(password)
        valid_verify = password == verify_password
        valid_email = (email == "") or EMAIL_RE.match(email)

        if valid_username and valid_password and valid_verify and valid_email:
            self.handle_valid_user(username, password, email)
        else:
            self.generate_signup({
                "username" : username if valid_username else "",
                "username_error" : "" if valid_username else "That's not a valid username.",
                "pw_error" : "" if valid_password else "That's not a valid password.",
                "verify_pw_error" : "" if not valid_password or valid_verify else "Your passwords didn't match.",
                "email" : email if valid_email else "",
                "email_error" : "" if valid_email else "That's not a valid email."
                })


class Welcome(jinjahandler.Handler):
    def get(self):
        self.render("signupOK.html", username=self.request.get("username"))
