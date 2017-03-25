from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, SelectField
from wtforms.validators import DataRequired

from Extractor.utils import DATE_FMT

VARTYPE_CHOICES = [
        ('typenull', 'typenull'), 
        ('typewind', 'typewind'), 
        ('typepres', 'typepres'),
        ('typetemp', 'typetemp'),
        ('typerad', 'typerad'),
]


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


class VariableForm(FlaskForm):
    var = StringField('var', validators=[DataRequired()])
    long_name = StringField('long_name', validators=[DataRequired()])
    units = StringField('units', validators=[DataRequired()])
    vartype = SelectField('vartype', choices=VARTYPE_CHOICES)
