import logging
import webapp2
import cloudstorage
import os
from google.appengine.api import app_identity
from wp import HomerNDB

def bucket_name():
    os.environ.get('BUCKET_NAME',app_identity.get_default_gcs_bucket_name())
    return app_identity.get_default_gcs_bucket_name()

def create_file(filename,content):
    """Create a file."""
    # The retry_params specified in the open call will override the default
    # retry params for this particular file handle.
    write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
    fn = "/" + bucket_name() + "/" + filename
    with cloudstorage.open(fn,'w',content_type='text/plain',retry_params=write_retry_params) as cloudstorage_file:
        for ln in content:
            cloudstorage_file.write(ln)
        cloudstorage_file.close()

def makefile():
    hdat = HomerNDB.query().fetch()
    printmat=[]
    for h in hdat:
        printmat.append(",".join(map(str,[h.player, h.gid, h.hr, h.month, h.pnum]))+"\n")
    create_file("homers2018",printmat)
    return printmat

class MainPage(webapp2.RequestHandler):
    def get(self):
        # do whatever needs to be done to the homer entities here
        z=makefile()
        self.response.write("Done")


utility = webapp2.WSGIApplication([('/', MainPage)], debug=True)
