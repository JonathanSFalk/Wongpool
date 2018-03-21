import webapp2
from google.appengine.ext import ndb
import logging
import mlbquery
import os
from google.appengine.api import app_identity, mail
import cloudstorage

from datetime import date


class HomerNDB(ndb.Model):
    player=ndb.StringProperty()
    gid=ndb.StringProperty()
    hr=ndb.IntegerProperty()
    month=ndb.IntegerProperty()
    pnum=ndb.IntegerProperty()
    date=ndb.StringProperty()

def makehomer(newhomer):
    bulkput = []
    newones = []
    for item in newhomer:
        dt = item[1][0:10]
        player=item[0]
        gid=item[1]
        hr=int(item[2])
        month=int(item[3])
        pnum=int(item[4])
        uniqueid = player+gid
        findit = HomerNDB.get_by_id(uniqueid)
        if findit is None:
            newHomer = HomerNDB(player=player,gid=gid,date=dt,hr=hr,month=month,pnum=pnum,id=uniqueid)
            bulkput.append(newHomer)
            newones.append([player,gid,hr,month,pnum])
    keylist = ndb.put_multi_async(bulkput)
    return newones

def bucket_name():
    os.environ.get('BUCKET_NAME',app_identity.get_default_gcs_bucket_name())
    return app_identity.get_default_gcs_bucket_name()


def gethomers(df,dt,pnames):
#takes a starting state and an end date and returns a list of Homer instances
    dinmonth = (0,0,31,30,31,30,31,31,30,0,0,0)
    mfrom=df.month
    dfrom=df.day
    mto=dt.month
    dto=dt.day
    newhomers=[]
    for m in range(mfrom,mto+1):
        for j in range(1,dinmonth[m-1]+1):
            if (m==mfrom and j<dfrom) or (m==mto and j>dto):
                pass
            else:
                dstring = str(m).zfill(2) + "/" + str(j).zfill(2)
#                logging.info('Sending ' +  dstring)
                dayhomers=addaday(dstring,pnames)
                for d in dayhomers:
                    newhomers.append(d)
    return newhomers

def addaday(day,pnames):
    logging.info('Adding: {0}'.format(day))
    toadd = mlbquery.hrthisday(pnames.keys(),day)
    m = int(day[0:2])
    if m == 3:
        m = 4
    if m == 10:
        m = 9
    entryadd = []
    if len(toadd) > 0:
        for x in toadd:
            entryadd.append([str(x[0]),str(x[1]),str(x[2]),str(m),pnames[x[0]]])
    return entryadd

def read_file(filename):
    if os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine/'):
        fn = "/" + bucket_name() + "/" + filename
        with cloudstorage.open(fn) as cloudstorage_file:
            lines = []
            for line in cloudstorage_file:
                lines.append(line.rstrip("\n\r"))
    else:
        fn = "data/" + filename
        with open(fn,"r") as cloudstorage_file:
            lines = []
            for line in cloudstorage_file:
                lines.append(line.rstrip("\n\r"))
    return lines

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

class UpdateJob(webapp2.RequestHandler):
    def get(self):
        today = date.today()
        allhomers = HomerNDB.query().fetch()
        # Generic adjustments here
        # for example
        #
        #        for q in qry:
        #            z=q.key.delete

        hlist=[]
#        for h in homerfile:
#            hlist.append(h.split(","))
        for h in allhomers:
            hlist.append([h.player,h.gid,h.hr,h.month,h.pnum])
        gidmax = max([x[1] for x in hlist])
        self.response.write("Maxdate: " + gidmax + "<br>")
#        logging.debug(gidmax)
        gidmax = date(2018,int(gidmax[5:7]),int(gidmax[8:10]))
        playerfile=read_file("players2018.csv")
        pnames={}
        for p in playerfile:
            ps = p.split(",")
            pnames[ps[1]]=ps[0]
        newhomers = gethomers(gidmax,today,pnames)
        self.response.write("Homers In<br>")
        for h in newhomers:
            self.response.write(repr(h)+"<br>")
        newhomers = makehomer(newhomers)
        self.response.write("Homers Out<br>")
        for h in newhomers:
            self.response.write(repr(h)+"<br>")
        hlist.extend(newhomers)
        tosave=[]
        for h in hlist:
            tosave.append(",".join(map(str,h)) +"\n")
        create_file("homers2018",tosave)

        nhl = []
        for nh in newhomers:
            if str(nh[2])=='1':
                num=""
            else:
                num="(" + str(nh[2]) + ")"
            nhl.append(nh[0] + num)
        nhl = " ,".join(nhl)

        mail.send_mail(sender='jonathansfalk@gmail.com',
                   to="jonathan.falk@marginalutilityllc.com",
                   subject="Update of Wongpool",
                   body= "Program ran on " + date.today().strftime("%b-%d") + ". Homers hit by: " + nhl)

        self.response.write("Done")

admin = ndb.toplevel(webapp2.WSGIApplication([(r'/admin', UpdateJob),],debug=True))
