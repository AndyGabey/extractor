from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class DatasetForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    long_name = StringField('long_name', validators=[DataRequired()])
    start_date_ts = StringField('start_date_ts', validators=[DataRequired()])
    end_date_ts = StringField('end_date_ts', validators=[DataRequired()])
    time_res = StringField('time_res', validators=[DataRequired()])
    file_fmt = StringField('file_fmt', validators=[DataRequired()])
    date_col_name = StringField('date_col_name', validators=[DataRequired()])
    time_col_name = StringField('time_col_name', validators=[DataRequired()])
    datetime_fmt = StringField('datetime_fmt', validators=[DataRequired()])
