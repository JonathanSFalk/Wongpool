import logging
from datetime import date, timedelta
from google.appengine.ext import ndb
import os
import cloudstorage
from google.appengine.api import app_identity

class HomerNDB(ndb.Model):
    player=ndb.StringProperty()
    gid=ndb.StringProperty()
    hr=ndb.IntegerProperty()
    month=ndb.IntegerProperty()
    pnum=ndb.IntegerProperty()
    date=ndb.StringProperty()
    timestamp=ndb.StringProperty()
    _use_cache = False
    _memcache_timeout=2

class Team:
    def __init__(self,data):
        self.wongid = int(data[0])
        self.name = data[1]
        self.players = [0,0,0,0,0,0,0,0]
        for j in range(0,8):
            self.players[j] = int(data[j + 2])
        self.tholder = 0

class Player:
    def __init__(self,data):
        self.wongid = int(data[0])
        self.name = data[1]
        self.fname = data[1][0:data[1].find(" ")]
        self.lname = data[1][data[1].find(" ") + 1:len(data[1])]
        self.lastfirst = self.lname + "," + self.fname
        self.lookup = int(data[2])


class Teamlist:
    def __init__(self,rowtype,contents):
        self.type = rowtype
        self.contents = contents


class PHM:
    def __init__(self,data):
        self.player = int(data[0])
        self.value = [0,0,0,0,0,0]
        for x in range(0,6):
            self.value[x] = int(data[x + 1])


def bucket_name():
    os.environ.get('BUCKET_NAME',app_identity.get_default_gcs_bucket_name())
    return app_identity.get_default_gcs_bucket_name()


def read_file(filename):
    if os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine/'):
        fn = "/" + bucket_name() + "/" + filename
        with cloudstorage.open(fn) as cloudstorage_file:
            lines = []
            for line in cloudstorage_file:
                lines.append(line.rstrip("\n"))
    else:
        fn = "data/" + filename
        with open(fn,"r") as cloudstorage_file:
            lines = []
            for line in cloudstorage_file:
                lines.append(line.rstrip("\n"))
    return lines


def makenames(cls,filename):
    din = read_file(filename)
    dout = []
    for item in din:
        dout.append(cls(item.split(",")))
    return dout

def listhomers(df,dt):
    datealphas = '2018_' + '{:02d}'.format(df.month) + "_" + '{:02d}'.format(df.day)
    datealphat = '2018_' + '{:02d}'.format(dt.month) + "_" + '{:02d}'.format(dt.day)
    retmat=[]
    for x in hdat:
        if datealphas <= x.gid  <= datealphat:
            retmat.append([x.gid[5:10],x.player,x.hr])
    toprint = sorted(retmat,key= lambda x: x[1])
    return toprint

def hothomers():
    startdate = dmax - timedelta(days = 9)
    datealpha = '2018_' + '{:02d}'.format(startdate.month) + "_" + '{:02d}'.format(startdate.day)
    #    logging.info(datealpha)
    hot = []
    #    logging.info(hdat[0].gid)
    for x in hdat:
        if x.gid > datealpha:
            hot.append(x)
    #     logging.info("Howmmany?" + str(len(hot)))
    pt = {}
    for p in pdat:
        pt[p.name] = sum([x.hr for x in hot if x.pnum == p.wongid])
    toprint = sorted(pt.iteritems(),key=lambda x: -x[1])
    return toprint[0:10]


def playerstoteams():
    ptoteams = {}
    for p in pdat:
        ptoteams[p.name] = ['Null']
        for t in tdat:
            if p.wongid in t.players:
                if ptoteams[p.name] == ['Null']:
                    ptoteams[p.name]=[t.name]
                else:
                    ptoteams[p.name].append(t.name)
    retmat = ptoteams.items()
    retmat.sort(key=lambda x: len(x[1]),reverse=True)
    retmat = [row for row in retmat if row[1] != ['Null']]

    return retmat

def getresults():
    results = []
    months = ("April: ","May: ","June: ","July: ","Aug: ","Sept: ")
    # Create monthly winners: results code 1
    for i in range(4,min(dmax.month,10)):
        standings = monthstandings(i)
        best = standings[0][2]
        winners = [x[1] + " (" + str(x[2]) + ")" for x in standings if x[2] == best]
        results.append([1,months[i - 4] + ", ".join(winners)])
    # create Current month standings: results code 2
    standings = monthstandings(min(max(dmax.month,4),9))
    results.extend(top5(2,standings))
#    for i in range(1,6):
#        results.append([2,standings[i-1][1] + ":  " + str(standings[i-1][2])])
#    fifth = standings[4][2]
#    n = 5
#    ties = [standings[4][1]]
#    while (standings[n][2] == fifth) and (n<len(standings)-1):
#        logging.info(repr(standings[n]))
#        ties.append(standings[n][1])
#        n = n + 1
#    if 1 < len(ties) <4:
#        results[len(results) - 1][1] = ",".join(ties)
#    elif len(ties)>1:
#        results[len(results) - 1][1] = str(len(ties)) + " entries tied at " + str(fifth)

    # Create Total standings: results code 3
    standings = monthstandings("Total")
    results.extend(top5(3,standings))
#    for i in range(1,6):
#        results.append([3,standings[i-1][1] + ":  " + str(standings[i-1][2])])
#    fifth = standings[4][2]
#    n = 5
#    ties = [standings[4][1]]
#    while (standings[n][2] == fifth) and (n<len(standings)-1):
#        logging.debug(repr(standings[n]))
#        ties.append(standings[n][1])
#        n += 1
#    if 1 < len(ties) <4:
#        results[len(results) - 1][1] = ",".join(ties)
#    elif len(ties)>1:
#        results[len(results) - 1][1] = str(len(ties)) + " entries tied at " + str(fifth)
    return results

def entrytable(sortcol):
    q = tdat
    if sortcol == 0:
        q.sort(key=lambda x: x.wongid)
    elif sortcol == 1:
        q.sort(key=lambda x: x.name)
    elif 2 <= sortcol < 8:
        for i in range(0,len(tdat)):
            tdat[i].tholder = total(tdat[i].wongid,sortcol + 2)
        q.sort(key=lambda x: -x.tholder)
    elif sortcol == 8:
        for i in range(0,len(tdat)):
            tdat[i].tholder = total(tdat[i].wongid,"Total")
        q.sort(key=lambda x: -x.tholder)
    tabout = []
    for x in q:
        obj = Teamlist("Team",str(x.wongid))
        tabout.append(obj)
        obj = Teamlist("Name",x.name)
        tabout.append(obj)
        pl = x.players
        for p in pl:
            pname = pnums[p]
            obj = Teamlist("Player",str(p).rjust(3) + "    " + pname.ljust(25))
            tabout.append(obj)
            for m in range(4,10):
                tabout.append(Teamlist("Month",phmdat[p][m - 4]))
            tabout.append(Teamlist("Total",sum(phmdat[p])))
        tabout.append(Teamlist("Player","Total"))
        for m in range(4,10):
            tabout.append(Teamlist("Month",total(x.wongid,m)))
        tabout.append(Teamlist("Total",total(x.wongid,"Total")))
    return tabout

def top6of8(listof8):
    assert len(listof8) == 8,"Gotta send 8"
    z = sorted(listof8,reverse=True)
    return z[0] + z[1] + z[2] + z[3] + z[4] + z[5]

def teamnoplay(sortcol):
    q = tdat
    if sortcol == 0:
        q.sort(key=lambda x: x.wongid)
    elif sortcol == 1:
        q.sort(key=lambda x: x.name)
    elif 2 <= sortcol < 8:
        for i in range(0,len(tdat)):
            tdat[i].tholder = total(tdat[i].wongid,sortcol + 2)
        q.sort(key=lambda x: -x.tholder)
    elif sortcol == 8:
        for i in range(0,len(tdat)):
            tdat[i].tholder = total(tdat[i].wongid,"Total")
        q.sort(key=lambda x: -x.tholder)
    retmat=[]
    for t in q:
        retmat.append([t.wongid,t.name,total(t.wongid,4),total(t.wongid,5),total(t.wongid,6),total(t.wongid,7),total(t.wongid,8),total(t.wongid,9),total(t.wongid,"Total")])
    return retmat

def total(team,month):
    # Month is Numeric except for "Total"
    #    logging.info(str(team)+":"+str(month))
    q = [x for x in tdat if x.wongid == team]
    plist = q[0].players
    mlist = []
    for j in plist:
        if month <> "Total":
            if j==0:
                logging.error("Team:"+str(q[0].wongid) + "Player:" + str(j) + "M:" + str(month-4))
            mlist.append(phmdat[j][month - 4])
        else:
            mlist.append(sum(phmdat[j]))
    return top6of8(mlist)

def monthstandings(month):
    # makes standings for month.  Last Month is called "Total"
    mstandings = []
    teamsort = sorted([x.name for x in tdat])
    for t in tdat:
        mstandings.append([t.wongid,t.name,total(t.wongid,month)])
    return sorted(mstandings,key=lambda x: (-x[2] * 10000 + teamsort.index(x[1])))

def top5(rowtype,standlist):
    # makes an appropriate list from a sorted standing list
    best = standlist[0][2]
    tiercount = [len([x for x in standlist if x[2]==best])]
    while sum(tiercount)<5:
        best=standlist[sum(tiercount)][2]
        tiercount.append(len([x for x in standlist if x[2]==best]))
    index = 0
    result=[]
    for i in tiercount:
        for j in range(index,index+i):
            result.append([rowtype,str(index+1)+". " + standlist[j][1] + " " + str(standlist[j][2])])
        index = index + i
    return result

def makephm(pdat,hdat):
    phmdat= {}
    for p in pdat:
        phmvec = [0,0,0,0,0,0]
        for m in range(0,6):
            phmvec[m] = sum([x.hr for x in hdat if x.pnum == p.wongid and x.month == m + 4])
        phmdat[p.wongid] = phmvec
    return phmdat

def makehdat():
    return HomerNDB.query(ancestor=ndb.Key('Project','Wong')).fetch(use_cache=False)

def init(pfname,tfname):

    # Read in all the data
    pdat = makenames(Player,pfname)
    hdat = makehdat()
# if there are no homers, restart the database
#    if len(hdat)==0:
#        from update import makehomer,gethomers
#        pnames = {}
#        for p in pdat:
#            pnames[p.name] = p.wongid
#        newhomers = gethomers(date(2018,3,17),date.today(),pnames)
#        makehomer(newhomers)
#        hdat = HomerNDB.query().fetch()
    tdat = makenames(Team,tfname)
    if len(hdat)>0:
        dmax = max([h.gid for h in hdat])
        dmaxstr = date(int(dmax[0:4]),int(dmax[5:7]),int(dmax[8:10])).strftime("%B %d").lstrip("0").replace(" 0"," ")
        dmax = date(int(dmax[0:4]),int(dmax[5:7]),int(dmax[8:10]))
    else:
        dmaxstr = "3/28"
        dmax = date(2018,3,28)

    phmdat = makephm(pdat,hdat)

    pnames = {}
    for p in pdat:
        pnames[p.name] = p.wongid

    pnums = {}
    for p in pdat:
        pnums[p.wongid] = p.name

    psort = {}
    x = sorted(pdat,key=lambda xx: xx.lastfirst)
    for i in range(1,len(x) + 1):
        psort[x[i - 1].name] = i

#    rpsort = dict([[v,k] for k,v in psort.items()])
# if needed, rpsort will be last return from init

    return [pdat,hdat,tdat,phmdat,dmax,dmaxstr,pnames,pnums,psort]

pfname="players2018.csv"
tfname="teams2018.csv"
# phfname="phmdat"
pdat,hdat,tdat,phmdat,dmax,dmaxstr,pnames,pnums,psort = init(pfname,tfname)
