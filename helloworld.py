import webapp2
  
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, Udacity!')




app = webapp2.WSGIApplication([
    ('/assignment-1/helloworld', MainPage),
], debug=True)