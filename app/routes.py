from google.appengine.ext import ndb,deferred
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, TwoDatesForm,  GetPSortField, GetTSortField
from flask_login import current_user, login_user, login_required
from app.models import User
import wp
import cfg
import logging
import models

@app.route('/')
@app.route('/index')
def index():
    results = ['April','#1','#1'],['May','#2','#2'],['June','#3','#3'],['July','#4','#4'],['August','#5','#5'],['September','',''],['Total','','']
    return render_template('home.html',rows=results, dmax=wp.dmax)

@app.route('/Current')
@app.route('/current')
def current():
    prows=wp.monthstandings(cfg.thismonth)
    return render_template('current.html', title='Current Standings', rows=prows, month="Total", dmax=wp.dmaxstr)

@app.route('/Teams', methods=['GET','POST'])
@app.route('/teams', methods=['GET','POST'])
def teams():
    form = GetTSortField()
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
    form= GetPSortField()
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

@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    form = TwoDatesForm()
    if form.is_submitted():
        logging.info(repr(form.datestart.data) + " " + repr(form.dateend.data))
        wp.gethomers(wp.pdat,form.datestart.data,form.dateend.data)
    return render_template('admin.html',form=form, dmax=wp.dmaxstr)

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

