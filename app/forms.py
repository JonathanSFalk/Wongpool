from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired,ValidationError,NumberRange
from wtforms.fields.html5 import DateField
import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired])
    password = PasswordField('Password', validators=[DataRequired])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

def validate_date(form,field):
    if field.data.year != 2018:
        raise ValidationError('Year Must be 2018')

class GetSortField(FlaskForm):
    rbtnp = SubmitField("Player")
    rbtntm = SubmitField("Team")
    rbtnno = SubmitField("#")
    rbtn1 =  SubmitField("April")
    rbtn2 = SubmitField("May")
    rbtn3 =  SubmitField("June")
    rbtn4 =  SubmitField("July")
    rbtn5 =  SubmitField("August")
    rbtn6 =  SubmitField("September")
    rbtnt =  SubmitField("Total")
    rbtnd = SubmitField("Go")
    datestart= DateField('Starting Date',default=datetime.date(2018,03,29),validators=[validate_date])
    datenum= IntegerField('Days',default=1,validators=[NumberRange(min=1)])
    rbtndt = SubmitField("Date")

