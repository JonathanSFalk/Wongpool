import webapp2
from google.appengine.api import mail
import logging
import cfg
import mlbquery

from datetime import date, timedelta


import os
import cloudstorage

from google.appengine.api import app_identity


class Homer:
    def __init__(self,data):
        self.player=data[0]
        self.gid=data[1]
        self.hr=int(data[2])
        self.month=int(data[3])
        self.pnum = int(data[4])


class Team:
    def __init__(self, data):
        self.wongid=int(data[1])
        self.name=data[0]
        self.players=[0,0,0,0,0,0,0,0]
        for j in range(0,8):
            self.players[j] = int(data[j+2])
        self.tholder=0

class Player:
    def __init__(self, data):
        self.wongid=int(data[0])
        self.name=data[1]
        self.fname=data[1][0:data[1].find(" ")]
        self.lname=data[1][data[1].find(" ")+1:len(data[1])]
        self.lastfirst = self.lname + "," + self.fname
        self.lookup = int(data[2])

class Teamlist:
    def __init__(self,rowtype,contents):
        self.type = rowtype
        self.contents = contents

class PHM:
    def __init__(self, data):
        self.player = int(data[0])
        self.value = [0,0,0,0,0,0]
        for x in range(0,6):
            self.value[x]=int(data[x+1])

def bucket_name():
    os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    return app_identity.get_default_gcs_bucket_name()

def create_file(filename,content):
    """Create a file."""
    # The retry_params specified in the open call will override the default
    # retry params for this particular file handle.
    write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
    fn = "/" + bucket_name() + "/" + filename
    with cloudstorage.open(
        fn, 'w', content_type='text/plain',retry_params=write_retry_params) as cloudstorage_file:
        for ln in content:
            cloudstorage_file.write(ln)
        cloudstorage_file.close()


def read_file(filename):
    fn = "/" + bucket_name() + "/" + filename
#    logging.debug("Reading" + fn)
    with cloudstorage.open(fn) as cloudstorage_file:
        lines=[]
        for line in cloudstorage_file:
            lines.append(line.rstrip("\n"))
        return lines

def read_file_local(filename):
    fn = filename
    with open(fn,"r") as cloudstorage_file:
        lines=[]
        for line in cloudstorage_file:
            lines.append(line.rstrip("\n"))
        return lines

def makenames(cls,filename):
    if cfg.local_dev:
        din = read_file_local(filename)
    else:
        din = read_file(filename)
    dout=[]
    for item in din:
        dout.append(cls(item.split(",")))
    return dout

def updatehomers_and_phm(newhomers,hdat, phmdat):
    tohfile=[]
    for h in newhomers:
#        logging.info("Number: {}  GID:  {}".format(str(h.pnum),h.gid))
        # Make sure this isn't a duplicate home run row
        if len([x for x in hdat if x.pnum==h.pnum and x.gid==h.gid])==0:
            tohfile.append(",".join([h.player,str(h.pnum),h.gid,str(h.hr),str(h.month)])+"\n")
            entry = phmdat[pnames[h.player]]
            entry[h.month-4] += h.hr
            phmdat[pnames[h.player]]=entry
    if cfg.local_dev:
        homers=read_file_local("homerbase")
    else:
        homers = read_file_local("homerbase")
    homers.extend(tohfile)
    create_file("homers", homers)
    tophmfile=[]
    for k,v in phmdat.items():
        vstr = [str(x) for x in v]
        tophmfile.append(str(k) + "," + ",".join(vstr) + "\n")
        create_file("phmdat",tophmfile)

def gethomers(pdat,df,dt,pnames):
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
                logging.info('Sending ' +  dstring)
                dayhomers=addaday(dstring,pnames)
                for d in dayhomers:
                    newhomers.append(d)
    return newhomers


def addaday(day,pnames):
    logging.info('Adding: {0}'.format(day))
    toadd = mlbquery.hrthisday(pnames.keys(),day)
    m = int(day[0:2])
    if m==3:
        m=4
    if m==10:
        m=9
    entryadd=[]
    if len(toadd)>0:
        for x in toadd:
            logging.info("0 {} 1 {} 2 {})".format(str(x[0]),str(x[1]),str(x[2])))
            entryadd.append(Homer([x[0],x[1],x[2],m,pnames[x[0]]]))
    return entryadd


class UpdateJob(webapp2.RequestHandler):
    def post(self):
        self.abort(200, headers=[('Allow', 'GET')])

    def get(self):
        if 'X-AppEngine-Cron' not in self.request.headers:
            self.error(403)

        today = date.today()
        # read in the data
        pdat = makenames(Player, "players2018")
        hdat = makenames(Homer, "homerbase")
        tdat = makenames(Team, "entries")
        phmitems = makenames(PHM, "phmdat")

        # now make 3 dictionaries
        phmdat = {}

        if len(phmitems) < len(pdat):
            for p in pdat:
                phmvec = [0, 0, 0, 0, 0, 0]
                for m in range(0, 6):
                    phmvec[m] = sum([x.hr for x in hdat if x.pnum == p.wongid and x.month == m + 4])
                phmdat[p.wongid] = phmvec
            #        print("Adding: " + str(p.wongid) + ":" + str(phmvec[0]) )
            tophmfile = []
            for k, v in phmdat.items():
                vstr = [str(x) for x in v]
                tophmfile.append(str(k) + "," + ",".join(vstr) + "\n")
            if cfg.local_dev:
                create_file_local("phmdat", tophmfile)
            else:
                create_file("phmdat", tophmfile)

        else:
            for p in phmitems:
                phmdat[p.player] = p.value

        pnames = {}
        for p in pdat:
            pnames[p.name] = p.wongid

        pnums = {}
        for p in pdat:
            pnums[p.wongid] = p.name

        teamsort = {}
        x = sorted(tdat, key=lambda xx: xx.name)
        for i in range(1, len(x) + 1):
            teamsort[x[i - 1].name] = i

        psort = {}
        x = sorted(pdat, key=lambda xx: xx.lastfirst)
        for i in range(1, len(x) + 1):
            psort[x[i - 1].name] = i

        rpsort = dict([[v, k] for k, v in psort.items()])

        logging.info("Got to here")

        dmax = max(hdat, lambda x: x.gid)
        dmax = dmax[0].gid

        maxdate = date(int(dmax[0:4]), int(dmax[5:7]), int(dmax[8:10]))

        year = maxdate.year

        if year == 2018:
            newhomers = gethomers(pdat, maxdate, today, pnames)
        else:
            newhomers = gethomers(pdat, maxdate, maxdate + timedelta(days=2),pnames)

        logging.info("Passed Newhomers")

        updatehomers_and_phm(newhomers, hdat, phmdat)

        logging.info("Done")

admin = webapp2.WSGIApplication([(r'/', UpdateJob),], debug=True)




