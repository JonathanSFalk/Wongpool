
with open("players","r") as f:
    pnames=f.readlines()
with open("homerfile") as f:
    homers=f.readlines()
with open("entries") as f:
    entries=f.readlines()
nmat=[]
hrmat=[]


def phomers(player,month):
    return poolplayers[player+str(month)]
#entries TeamName PlayerNum TeamNum

teamdictplayers={}
teamdictnames={}
numteams=len(entries)/8
for i in range(numteams):
    idx=i*8
    mems=[]
    key=int(entries[idx][47:50].strip())
    teamdictnames[key]=entries[idx][0:30].lstrip()
    for j in range(idx,idx+8,1):
        mems.append(int(entries[j][38:41].strip()))
    teamdictplayers[key]=mems


# nmat Player# PlayerLName PlayerFname
for p in pnames:
    nmat.append(p.split())
nmat=[row[0:3] for row in nmat]

#hrmat PlayerId hrdatemmdd hrmo
for l in homers:
    l=l.replace('"','')
    hrmat.append(l.split())
hrmat=[row[0:3] for row in hrmat]

#Derive playerIds and put them in nmat
for n in nmat:
    idx=nmat.index(n)
    nmat[idx] = n + [(n[1][0:4]+n[2][0]+"001").lower()]
    nmat[idx][1] = nmat[idx][1][:-1]
nameguess=map(lambda col1:col1[3],nmat)
allnames =map(lambda col0:col0[0],hrmat)
for idx,item in enumerate(nameguess):
    titem = item
    if titem not in allnames:
        while titem not in allnames and titem[7] != "9":
            titem = item[0:7]+str(int(titem[7])+1)
    nameguess[idx]=titem
    nmat[idx][3]=titem
    if nameguess[idx]=="stang009":
        nmat[idx][3]="stanm004"
        nameguess[idx]="stanm004"
# poolplayers is a dictionary with key PlayerIdMonth and value homeruns hit in that month in hrmat
poolplayers={}
for n in nmat:
    for j in range(4,10):
        z=n[3]+str(j)
        poolplayers.update({z:0})
for h in hrmat:
    if h[0]+"4" in poolplayers:
        z=str(h[2])
        if z=="3" : z="4"
        if z=="10": z="9"
        poolplayers[h[0]+z] += 1



def printplayertable():
    print "     Player                  ","Apr","May","Jun","Jul","Aug","Sep","Total"
    for i in pnames:
        idx=pnames.index(i)
        ncode=nameguess[idx]
        print i[0:27],
        t=0
        widths = (7,3,3,3,3,3)
        for i in range(4,10):
            print repr(phomers(ncode,i)).rjust(widths[i-4]),
            t += phomers(ncode,i)
        print repr(t).rjust(5)

def printentrytable():
    tnums=teamdictnames.keys()
    tnums.sort()
    widths = (7,3,3,3,3,3)
    print "Team          Player                       ", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Total"
    for i in tnums:
        print teamdictnames[i]
        pnums=teamdictplayers[i]
        pnums.sort()
        for j in range(8):
            t=0
            playernum = pnums[j]
            prow=[item for item in nmat if item[0]==str(playernum)]
            width = len(prow[0][1])+len(prow[0][2])
            print repr(playernum).rjust(10),prow[0][2],prow[0][1]," "*(25-width),
            for k in range(4,10):
                print repr(poolplayers[prow[0][3]+str(k)]).rjust(widths[k-4]),
                t += poolplayers[prow[0][3]+str(k)]
            print repr(t).rjust(5)
        print



printentrytable()










