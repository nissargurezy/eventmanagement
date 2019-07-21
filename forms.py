from flask_wtf import FlaskForm
from wtforms import DateTimeField,validators
from wtforms.validators import InputRequired
from datetime import datetime




class log(FlaskForm):
    stime = DateTimeField(label='Start time(EDT)',validators=[validators.InputRequired()],format = "%d%b%Y %H:%M",default= datetime.utcnow)
