import webapp2
from google.appengine.api import mail
import logging
import mlbquery

from datetime import date, timedelta
from wp import Homer, create_file, read_file, init

def updatehomers_and_phm(hfname, newhomers,hdat, phmdat, pnames):
    tohfile=[]
    for h in newhomers:
        # Make sure this isn't a duplicate home run row
        if len([x for x in hdat if x.pnum==h.pnum and x.gid==h.gid])==0:
            tohfile.append(",".join([h.player,h.gid,str(h.hr),str(h.month),str(h.pnum)])+"\n")
            entry = phmdat[pnames[h.player]]
            entry[h.month-4] += h.hr
            phmdat[pnames[h.player]]=entry
    homers=read_file(hfname)
    dout=[]
    for din in homers:
        dout.append(din + "\n")
    dout.extend(tohfile)
    create_file("homers", dout)
    tophmfile=[]
    for k,v in phmdat.items():
        vstr = [str(x) for x in v]
        tophmfile.append(str(k) + "," + ",".join(vstr) + "\n")
    create_file("phmdat",tophmfile)

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
                logging.info('Sending ' +  dstring)
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
            entryadd.append(Homer([x[0],x[1],x[2],m,pnames[x[0]]]))
    return entryadd


class UpdateJob(webapp2.RequestHandler):
    def get(self):
        if 'X-AppEngine-Cron' not in self.request.headers:
            self.error(403)
        today = date.today()
        pfname = "players2018.csv"
        hfname = "homerbase"
        tfname = "entries"
        phfname = "phmdat"

        pdat,hdat,tdat,phmdat,dmax,dmaxstr,pnames,pnums,psort,rpsort = init(pfname,hfname,tfname,phfname)

        logging.info("Got to here")

        dmax = max([h.gid for h in hdat])

        maxdate = date(int(dmax[0:4]), int(dmax[5:7]), int(dmax[8:10]))

        year = maxdate.year

        if year == 2018:
            newhomers = gethomers(maxdate, today, pnames)
        else:
            newhomers = gethomers(maxdate, maxdate + timedelta(days=2),pnames)

        logging.info("Passed Newhomers")

        updatehomers_and_phm(hfname, newhomers, hdat, phmdat, pnames)

        nhl = []
        for nh in newhomers:
            if nh.hr==1:
                num=""
            else:
                num="(" + str(nh.hr) + ")"
            nhl.append(nh.player + num)
        nhl = " ,".join(nhl)

        logging.info("Done")

        mail.send_mail(sender='jonathansfalk@gmail.com',
                   to="jonathan.falk@marginalutilityllc.com",
                   subject="Update of Wongpool",
                   body= "Program ran on " + date.today().strftime("%b-%d") + ". Homers hit by: " + nhl)

        self.response.write("Done")


admin = webapp2.WSGIApplication([(r'/admin', UpdateJob),], debug=True)




