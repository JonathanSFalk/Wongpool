from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, TwoDatesForm,  GetSortField
from flask_login import current_user, login_user, login_required
import datetime
import wp
import cfg
import logging
import models


@app.route('/')
@app.route('/index')
def index():
    results = wp.getresults()
    mstands = [x[1] for x in results if x[0]==1]
    cstands = [x[1] for x in results if x[0]==2]
    tstands = [x[1] for x in results if x[0]==3]
    return render_template('home.html',mstand=mstands, cstand=cstands, tstand=tstands, dmax=wp.dmaxstr)

@app.route('/Standings', methods=['GET','POST'])
@app.route('/standings', methods=['GET','POST'])
def standings():
    form = GetSortField()
    if form.is_submitted():
        sortcol = 2*form.rbtn1.data + 3*form.rbtn2.data + 4*form.rbtn3.data + 5*form.rbtn4.data + 6*form.rbtn5.data + 7*form.rbtn6.data + 8*form.rbtnt.data + 0*form.rbtnno.data + 1*form.rbtntm.data
        sortcol = int(sortcol)
#        logging.info("SORTCOL" + str(sortcol))
    else:
        sortcol = 1
    prows=wp.teamnoplay(sortcol)
    return render_template('standings.html', title='Standings', form=form, rows=prows, dmax=wp.dmaxstr)

@app.route('/Teams', methods=['GET','POST'])
@app.route('/teams', methods=['GET','POST'])
def teams():
    form = GetSortField()
    if form.is_submitted():
        sortcol = 2*form.rbtn1.data + 3*form.rbtn2.data + 4*form.rbtn3.data + 5*form.rbtn4.data + 6*form.rbtn5.data + 7*form.rbtn6.data + 8*form.rbtnt.data + 0*form.rbtnno.data + 1*form.rbtnp.data
        sortcol = int(sortcol)
        logging.info("SORTCOL" + str(sortcol))
    else:
        sortcol = 1
    logging.info("Sortcol: "+str(sortcol))
    prows=wp.entrytable(sortcol)
    return render_template('teams.html', title='Team Standings', rows=prows, form=form, dmax=wp.dmaxstr)

@app.route('/Hot', methods=['GET','POST'])
@app.route('/hot', methods=['GET','POST'])
def hot():
    prows=wp.hothomers()
    return render_template('hot.html', title="Who's Hot", rows=prows,  dmax=wp.dmaxstr)

@app.route('/ptt', methods=['GET','POST'])
def ptt():
    prows=wp.playerstoteams()

    return render_template('ptoteams.html', title="Player->Teams", rows=prows,  dmax=wp.dmaxstr)

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
        sortcol = 10
    pmat=[]
    data=wp.pdat
    names = wp.pnums
    ph = wp.phmdat
    ps = wp.psort
    for p in data:
        n=p.wongid
#        pmat.append([n,names[n],ph[n][0],ph[n][1],ph[n][2],ph[n][3],ph[n][4],ph[n][5],sum(ph[n])])
        pmat.append([n,names[n],ph[n][0],ph[n][1],ph[n][2],ph[n][3],ph[n][4],ph[n][5],sum(ph[n]),p.lookup,-n,-ps[names[n]]])
    pmat.sort(key=sk)
    return render_template('players.html', title='Player Results', rows=pmat, form=form, dmax = wp.dmaxstr)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.poolboss
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, dmax=wp.dmaxstr)

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
        return render_template('homers.html',form=form,toprint=toprint,dmax=wp.dmaxstr, sortfield=sortfield)
    else:
        return render_template('homers.html',form=form,dmax=wp.dmaxstr)


