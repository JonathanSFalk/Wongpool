import logging
from datetime import date, timedelta

import os
import cloudstorage

from google.appengine.api import app_identity


class Homer:
    def __init__(self,data):
        self.player = data[0]
        self.gid = data[1]
        self.hr = int(data[2])
        self.month = int(data[3])
        self.pnum = int(data[4])

class Team:
    def __init__(self,data):
        self.wongid = int(data[1])
        self.name = data[0]
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
    datealphas = '2017_' + '{:02d}'.format(df.month) + "_" + '{:02d}'.format(df.day)
    datealphat = '2017_' + '{:02d}'.format(dt.month) + "_" + '{:02d}'.format(dt.day)
    retmat=[]
    for x in hdat:
        if x.gid >= datealphas and x.gid <= datealphat:
            retmat.append([x.gid[5:10],x.player,x.hr])
    toprint = sorted(retmat,key= lambda x: x[1])
    return toprint

def hothomers():
    startdate = dmax - timedelta(days = 9)
    datealpha = '2017_' + '{:02d}'.format(startdate.month) + "_" + '{:02d}'.format(startdate.day)
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
    standings = monthstandings(min(dmax.month,9))
    for i in range(1,6):
        results.append([2,standings[i-1][1] + ":  " + str(standings[i-1][2])])
    fifth = standings[4][2]
    n = 5
    ties = [standings[4][1]]
    while (standings[n][2] == fifth) and (n<len(standings)-1):
#        logging.info(repr(standings[n]))
        ties.append(standings[n][1])
        n = n + 1
    if len(ties) > 1 and len(ties)<4:
        results[len(results) - 1][1] = ",".join(ties)
    elif len(ties)>1:
        results[len(results) - 1][1] = str(len(ties)) + " entries tied at " + str(fifth)
    # Create Total standings: results code 3
    standings = monthstandings("Total")
    for i in range(1,6):
        results.append([3,standings[i-1][1] + ":  " + str(standings[i-1][2])])
    fifth = standings[4][2]
    n = 5
    ties = [standings[4][1]]
    while (standings[n][2] == fifth) and (n<len(standings)-1):
#        logging.debug(repr(standings[n]))
        ties.append(standings[n][1])
        n += 1
    if len(ties) > 1 and len(ties)<4:
        results[len(results) - 1][1] = ",".join(ties)
    elif len(ties)>1:
        results[len(results) - 1][1] = str(len(ties)) + " entries tied at " + str(fifth)
    return results

def entrytable(sortcol):
    q = tdat
    if sortcol == 0:
        q.sort(key=lambda x: x.wongid)
    elif sortcol == 1:
        q.sort(key=lambda x: x.name)
    elif sortcol >= 2 and sortcol < 8:
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
    elif sortcol >= 2 and sortcol < 8:
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
#            logging.info("Team:"+str(q[0].wongid) + "Player:" + str(j) + "M:" + str(month-4))
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

def init(pfname,hfname,tfname,phfname):
    # Read in all the data
    pdat = makenames(Player,pfname)
    hdat = makenames(Homer,hfname)
    tdat = makenames(Team,tfname)
    phmitems = makenames(PHM,phfname)
    homersph = 0
    for ph in phmitems:
        homersph += sum(ph.value)
    homersh = sum([x.hr for x in hdat])

    dmax = max([h.gid for h in hdat])

    dmaxstr = date(int(dmax[0:4]),int(dmax[5:7]),int(dmax[8:10])).strftime("%B %d").lstrip("0").replace(" 0", " ")
    dmax = date(int(dmax[0:4]),int(dmax[5:7]),int(dmax[8:10]))
    # now make 3 dictionaries

    phmdat= {}
    if homersph != homersh:
        for p in pdat:
            phmvec = [0,0,0,0,0,0]
            for m in range(0,6):
                phmvec[m] = sum([x.hr for x in hdat if x.pnum == p.wongid and x.month == m + 4])
            phmdat[p.wongid] = phmvec
        #        print("Adding: " + str(p.wongid) + ":" + str(phmvec[0]) )
        tophmfile = []
        for k,v in phmdat.items():
            vstr = [str(x) for x in v]
            tophmfile.append(str(k) + "," + ",".join(vstr) + "\n")
        if os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine/'):
            create_file(phfname,tophmfile)
    else:
        for p in phmitems:
            phmdat[p.player] = p.value
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

    rpsort = dict([[v,k] for k,v in psort.items()])

    return [pdat,hdat,tdat,phmdat,dmax,dmaxstr,pnames,pnums,psort,rpsort]

pfname="players2018.csv"
hfname="homers"
tfname="entries"
phfname="phmdat"
pdat,hdat,tdat,phmdat,dmax,dmaxstr,pnames,pnums,psort,rpsort = init(pfname,hfname,tfname,phfname)
