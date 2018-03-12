from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired])
    password = PasswordField('Password', validators=[DataRequired])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class TwoDatesForm(FlaskForm):
    datestart=DateField('Starting Date')
    dateend=DateField('Ending Date')
    submit = SubmitField('Go')

class GetTSortField(FlaskForm):
    rbtnp = SubmitField("Team")
    rbtnno = SubmitField("#")
    rbtn1 =  SubmitField("April")
    rbtn2 = SubmitField("May")
    rbtn3 =  SubmitField("June")
    rbtn4 =  SubmitField("July")
    rbtn5 =  SubmitField("August")
    rbtn6 =  SubmitField("September")
    rbtnt =  SubmitField("Total")

class GetPSortField(FlaskForm):
    rbtnp = SubmitField("Team")
    rbtnno = SubmitField("#")
    rbtn1 =  SubmitField("April")
    rbtn2 = SubmitField("May")
    rbtn3 =  SubmitField("June")
    rbtn4 =  SubmitField("July")
    rbtn5 =  SubmitField("August")
    rbtn6 =  SubmitField("September")
    rbtnt =  SubmitField("Total")
