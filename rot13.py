import webapp2
import codecs


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
    ('/assignment-2/rot13', Rot13Page),
], debug=True)