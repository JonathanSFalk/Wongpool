from flask import render_template
from app import app
from app.forms import GetSortField
import datetime
import logging
import wp
from cfg import Config


@app.route('/')
@app.route('/index')
def index():
    lupdate = Config.LastUpdate
    updatecheck = Config()
    if updatecheck.lu > lupdate:
        Config.LastUpdate = updatecheck.lu
        wp.hdat = wp.makehdat()
        wp.phmdat = wp.makephm(wp.pdat,wp.hdat)
    results = wp.getresults()
    mstands = [x[1] for x in results if x[0]==1]
    cstands = [x[1] for x in results if x[0]==2]
    tstands = [x[1] for x in results if x[0]==3]
    return render_template('home.html',mstand=mstands, cstand=cstands, tstand=tstands, lu=lupdate,
                           rprint=max(len(mstands),len(cstands),len(tstands)))

@app.route('/Standings', methods=['GET','POST'])
@app.route('/standings', methods=['GET','POST'])
def standings():
    form = GetSortField()
    if form.is_submitted():
        sortcol = 2*form.rbtn1.data + 3*form.rbtn2.data + 4*form.rbtn3.data + 5*form.rbtn4.data + 6*form.rbtn5.data + 7*form.rbtn6.data + 8*form.rbtnt.data + 0*form.rbtnno.data + 1*form.rbtntm.data
        sortcol = int(sortcol)
#        logging.info("SORTCOL" + str(sortcol))
    else:
        sortcol = min(max(wp.dmax.month,4),9)-2
    prows=wp.teamnoplay(sortcol)
    return render_template('standings.html', title='Standings', form=form, rows=prows, lu=Config.LastUpdate)

@app.route('/Teams', methods=['GET','POST'])
@app.route('/teams', methods=['GET','POST'])
def teams():
    form = GetSortField()
    if form.is_submitted():
        sortcol = 2*form.rbtn1.data + 3*form.rbtn2.data + 4*form.rbtn3.data + 5*form.rbtn4.data + 6*form.rbtn5.data + 7*form.rbtn6.data + 8*form.rbtnt.data + 0*form.rbtnno.data + 1*form.rbtntm.data
        sortcol = int(sortcol)
        logging.info("SORTCOL" + str(sortcol))
    else:
        sortcol = min(max(wp.dmax.month,4),9)-2
    logging.info("Sortcol: "+str(sortcol))
    prows=wp.entrytable(sortcol)
    return render_template('teams.html', title='Team Standings', rows=prows, form=form, lu=Config.LastUpdate)

@app.route('/Hot', methods=['GET','POST'])
@app.route('/hot', methods=['GET','POST'])
def hot():
    prows=wp.hothomers()
    return render_template('hot.html', title="Who's Hot", rows=prows,  lu=Config.LastUpdate)

@app.route('/ptt', methods=['GET','POST'])
def ptt():
    prows=wp.playerstoteams()

    return render_template('ptoteams.html', title="Player->Teams", rows=prows, lu=Config.LastUpdate)

@app.route('/Players', methods=['GET','POST'])
@app.route('/players', methods=['GET','POST'])
def players():
    def sk(x):
        return -int(x[sortcol])
    form= GetSortField()
    if form.is_submitted():
        sortcol = 2*form.rbtn1.data + 3*form.rbtn2.data + 4*form.rbtn3.data + 5*form.rbtn4.data + 6*form.rbtn5.data + 7*form.rbtn6.data + 8*form.rbtnt.data + 10*form.rbtnno.data + 11*form.rbtnp.data
        sortcol = int(sortcol)
    else:
        sortcol = min(max(wp.dmax.month,4),9)-2
    pmat=[]
    data=wp.pdat
    names = wp.pnums
    ph = wp.phmdat
    ps = wp.psort
    for p in data:
        n=p.wongid
        pmat.append([n,names[n],ph[n][0],ph[n][1],ph[n][2],ph[n][3],ph[n][4],ph[n][5],sum(ph[n]),p.lookup,-n,-ps[names[n]]])
    pmat.sort(key=sk)
    return render_template('players.html', title='Player Results', rows=pmat, form=form, lu=Config.LastUpdate)

@app.route('/homers', methods=['GET','POST'])
def homers():
    form = GetSortField()
    if form.validate_on_submit():
        enddate = form.datestart.data + datetime.timedelta(days=form.datenum.data)
        whichbutton = form.rbtndt.data + 2*form.rbtnp.data + 3*form.rbtnd.data
        if whichbutton==1:
            toprint = sorted(wp.listhomers(form.datestart.data,enddate),key=lambda x: x[0])
            sortfield = "d"
        elif whichbutton==3:
            toprint = sorted(wp.listhomers(form.datestart.data,enddate),key= lambda x: x[0])
            sortfield = "d"
        else:
            toprint = sorted(wp.listhomers(form.datestart.data,enddate),key=lambda x: wp.psort[x[1]])
            sortfield = "p"
        return render_template('homers.html',form=form,toprint=toprint,dmax=wp.dmaxstr, sortfield=sortfield, lu=Config.LastUpdate)
    else:
        return render_template('homers.html',form=form,lu=Config.LastUpdate)


#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    if current_user.is_authenticated:
#        return redirect(url_for('index'))
#    form = LoginForm()
#    if form.validate_on_submit():
#        user = models.poolboss
#        if user is None or not user.check_password(form.password.data):
#            flash('Invalid username or password')
#            return redirect(url_for('login'))
#        login_user(user, remember=form.remember_me.data)
#        next_page = request.args.get('next')
#        if not next_page or url_parse(next_page).netloc != '':
#            next_page = url_for('index')
#        return redirect(next_page)
#    return render_template('login.html', title='Sign In', form=form, dmax=wp.dmaxstr)
