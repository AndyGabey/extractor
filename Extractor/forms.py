from flask_wtf import FlaskForm
from wtforms import (StringField, FloatField, PasswordField, DateTimeField,
                     SelectField, SelectMultipleField, BooleanField)
from wtforms.validators import DataRequired, Length

from Extractor.utils import DATE_FMT


class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


POPOVER_NAME = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Dataset ID" data-content="A unique identifier for this dataset, used when retrieving data. No spaces are allowed.">Dataset ID</a>'
POPOVER_LONG_NAME = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Dataset name" data-content="This is the &quot;friendly&quot; name or description of the dataset for human users to read">Dataset long name</a>'
POPOVER_START_DATE = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Start date" data-content="The earliest time for which data is available. <br /><b>Must</b> be in format {}">Start date</a>'.format(DATE_FMT)
POPOVER_END_DATE = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="End date" data-content="The final time for which data is available. <br /><b>Must be in format: {}</b>. <br />If the dataset is still being added to, choose a date far in the future">End date</a>'.format(DATE_FMT)
POPOVER_FILE_FORMAT = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="End date" data-content="Filename pattern using date placeholders: <ul><li>{{year}} = year</li><li>{{yday}} = day of year (001 to 365 or 366)</li><li>{{month}} = month (leading 0)</li><li>{{day}} = day (leading 0)</li></ul>Example: /mnt/data/fluxes/{{year}}/{{month}}/flux_{{day}}.csv">Filename pattern</a>'.format(DATE_FMT)
POPOVER_DATE = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Date/Datetime column" data-content="The name of the column containing date stamp, or combined date and timestamp">Date/datetime column name</a>'
POPOVER_TIME = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Time column" data-content="Optional: Name of a dedicated time column, if time is in a separate column to the date">Time column name (optional)</a>'
POPOVER_DATESTRING = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Timestamp format string" data-content="Format of date and/or time columns in standard format (i.e. %H%M%S). Leave a space between date and time formats if date and time are in separate columns">Timestamp format</a>'

class DatasetForm(FlaskForm):
    name = StringField(POPOVER_NAME, validators=[DataRequired()])
    long_name = StringField(POPOVER_LONG_NAME, validators=[DataRequired()])
    start_date = DateTimeField(POPOVER_START_DATE, format=DATE_FMT, validators=[DataRequired()])
    end_date = DateTimeField(POPOVER_END_DATE, format=DATE_FMT, validators=[DataRequired()])
    time_res = StringField('Rows of data per file', validators=[DataRequired()])
    file_fmt = StringField(POPOVER_FILE_FORMAT, validators=[DataRequired()])
    date_col_name = StringField(POPOVER_DATE, validators=[DataRequired()])
    time_col_name = StringField(POPOVER_TIME, validators=[])
    datetime_fmt = StringField(POPOVER_DATESTRING, validators=[DataRequired()])
    file_freq = SelectField('Daily or yearly files?', choices={("daily", 'Daily'), ("yearly", 'Yearly')}, validators=[DataRequired()])


VARTYPE_CHOICES = [
    ('typenull', 'Other'),
    ('typewind', 'Wind'),
    ('typerain', 'Precipitation'),
    ('typepres', 'Pressure'),
    ('typetemp', 'Temperature'),
    ('typerad', 'Radiation'),
]


class VariableForm(FlaskForm):
    _POPOVER_VARID = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Variable" data-content="Variable ID, as used in data file column headers">Variable ID</a>'
    _POPOVER_VARNAME = '<a href="#" data-html="true" data-toggle="popover" data-trigger="focus" title="Variable name" data-content="Description of the variable">Variable name</a>'
    var = StringField(_POPOVER_VARID, validators=[DataRequired()])
    long_name = StringField(_POPOVER_VARNAME, validators=[DataRequired()])
    units = StringField('Measurement units', validators=[DataRequired()])
    vartype = SelectField('Category', choices=VARTYPE_CHOICES)


class TokenForm(FlaskForm):
    token = StringField('User token', validators=[Length(max=10), DataRequired()])
    expiry_date = DateTimeField('expiry_date', validators=[DataRequired()])
    notes = StringField('notes', validators=[])
    max_request_time_hours = FloatField('max_request_time_hours', validators=[DataRequired()])
    max_request_rows = StringField('max_request_rows', validators=[DataRequired()])
    max_request_files = StringField('max_request_files', validators=[DataRequired()])
    dataset_ids = SelectMultipleField('datasets', coerce=int, choices=[], validators=[])
