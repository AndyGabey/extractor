from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length

from Extractor.utils import DATE_FMT

class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class DatasetForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    long_name = StringField('long_name', validators=[DataRequired()])
    start_date = DateTimeField('start_date', format=DATE_FMT, validators=[DataRequired()])
    end_date = DateTimeField('end_date', format=DATE_FMT, validators=[DataRequired()])
    time_res = StringField('time_res', validators=[DataRequired()])
    file_fmt = StringField('file_fmt', validators=[DataRequired()])
    date_col_name = StringField('date_col_name', validators=[DataRequired()])
    time_col_name = StringField('time_col_name', validators=[])
    datetime_fmt = StringField('datetime_fmt', validators=[DataRequired()])


VARTYPE_CHOICES = [
        ('typenull', 'typenull'), 
        ('typewind', 'typewind'), 
        ('typepres', 'typepres'),
        ('typetemp', 'typetemp'),
        ('typerad', 'typerad'),
]


class VariableForm(FlaskForm):
    var = StringField('var', validators=[DataRequired()])
    long_name = StringField('long_name', validators=[DataRequired()])
    units = StringField('units', validators=[DataRequired()])
    vartype = SelectField('vartype', choices=VARTYPE_CHOICES)


class TokenForm(FlaskForm):
    token = StringField('var', validators=[DataRequired()])
    expiry_date = DateTimeField('expiry_date', validators=[DataRequired()])
    notes = StringField('notes', validators=[])
    datasets = SelectMultipleField('datasets', coerce=int, choices=[], validators=[])
