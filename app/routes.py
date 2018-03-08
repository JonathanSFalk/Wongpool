from google.appengine.ext import ndb,deferred
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, TwoDatesForm
from flask_login import current_user, login_user, login_required
from app.models import User
import wp
import cfg
import logging


@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')

@app.route('/Current')
@app.route('/current')
def current():
    prows=wp.monthstandings(cfg.thismonth)
    return render_template('current.html', title='Current Standings', rows=prows, month="Total")

@app.route('/Teams')
@app.route('/teams')
def teams():
    prows=wp.entrytable()
    return render_template('teams.html', title='Team Standings', rows=prows)

@app.route('/Players')
@app.route('/players')
def players():
    pmat=[]
    data=wp.pdat
    for p in data:
        n=p.wongid
        pmat.append([n,p.fullname,wp.ph(n,4),wp.ph(n,5),wp.ph(n,6),wp.ph(n,7),wp.ph(n,8),wp.ph(n,9),wp.totalforplayer(n)])
        pmat.sort()
    return render_template('players.html', title='Player Results', rows=pmat)

@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    form = TwoDatesForm()
    if form.is_submitted():
        logging.info(repr(form.datestart.data) + " " + repr(form.dateend.data))
        deferred.defer(wp.makehomers,form.datestart.data,form.dateend.data)
    return render_template('admin.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query(User.username == form.username.data).get()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
