import webapp2
from google.appengine.ext import ndb
import logging
import mlbquery
import os
from google.appengine.api import mail,app_identity
import cloudstorage
from wp import HomerNDB
from datetime import date, datetime, timedelta
import pytz

class LastUpdate(ndb.Model):
    lu = ndb.StringProperty()
    _use_cache = False
    _memcache_timeout=2

def bucket_name():
    os.environ.get('BUCKET_NAME',app_identity.get_default_gcs_bucket_name())
    return app_identity.get_default_gcs_bucket_name()

def makehomer(newhomer):
    bulkput = []
    newones = []
    # ALL ITEMS IN THIS UPDATE GET THE SAME TIMESTAMP
    timestamp = datetime.utcnow().strftime("%b %d %H:%M UTC")
    for item in newhomer:
        dt = item[1][0:10]
        player=item[0]
        gid=item[1]
        hr=int(item[2])
        month=int(item[3])
        pnum=int(item[4])
        uniqueid = player+gid
        newHomer = HomerNDB(player=player,gid=gid,date=dt,hr=hr,month=month,pnum=pnum,timestamp=timestamp,id=uniqueid,
                            parent=ndb.Key('Project','Wong'))
        bulkput.append(newHomer)
        newones.append([player,gid,hr,month,pnum])
    ndb.put_multi(bulkput)
    return newones


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

class UpdateJob(webapp2.RequestHandler):
    def get(self):
        rightnow=datetime.now(pytz.timezone('America/New_York'))
        today = date(2018,rightnow.month,rightnow.day)
        # Generic adjustments here
        # for example
        #
        #        for q in qry:
        #            z=q.key.delete
        playerfile=read_file("players2018.csv")
        pnames={}
        for p in playerfile:
            ps = p.split(",")
            pnames[ps[1]]=ps[0]
        if rightnow.hour<12:
            newhomers = gethomers(today - timedelta(1),today,pnames)
        else:
            newhomers = gethomers(today,today,pnames)
        self.response.write("Homers In<br>")
        for h in newhomers:
            self.response.write(repr(h)+"<br>")
        newhomers = makehomer(newhomers)
        nhl = []
        for nh in newhomers:
            if str(nh[2])=='1':
                num=""
            else:
                num="(" + str(nh[2]) + ")"
            nhl.append(str(nh[0]) + num)
        nhl = "\n".join(nhl)

        mail.send_mail(sender='jonathansfalk@gmail.com',
                   to="webmaster@wongpool.com",
                   subject="Update of Wongpool",
                   body= "Program ran on " + date.today().strftime("%b-%d") + ". Homers hit by: \n" + nhl)

        lu = LastUpdate(lu=rightnow.strftime("%b %d %H:%M"),id=1,parent=ndb.Key('Project','Wong'))
        lu.put()
        self.response.write("Done")


update = ndb.toplevel(webapp2.WSGIApplication([(r'/', UpdateJob),],debug=True))
