import webapp2


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