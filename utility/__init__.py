import webapp2
import cloudstorage
import os
from google.appengine.api import app_identity
from google.appengine.ext import ndb
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
    hdat = HomerNDB.query(ancestor=ndb.Key('Project','Wong')).fetch()
    printmat=[]
    for h in hdat:
        printmat.append(",".join(map(str,[h.player, h.gid, h.hr, h.month, h.pnum]))+"\n")
    create_file("homers2018",printmat)
    return printmat

class MainPage(webapp2.RequestHandler):
    def get(self):
        # Dummy key for lastupdate
#        hdat = HomerNDB.query().fetch()
#        for h in hdat:
#            hdatnew = HomerNDB(player=h.player,gid=h.gid,hr=h.hr,month=h.month,pnum=h.pnum,date=h.date,timestamp=h.timestamp,
#                               id=h.player+h.gid, parent=ndb.Key('Project','Wong'))
#            hdatnew.put()
#        lu = ndb.Key(LastUpdate,1).get()
#        lu2 = LastUpdate(lu=lu.lu,id=1,parent=ndb.Key('Project','Wong'))
#        lu2.put()
        # do whatever needs to be done to the homer entities here
        makefile()
        self.response.write("Done")


utility = webapp2.WSGIApplication([('/', MainPage)], debug=True)
