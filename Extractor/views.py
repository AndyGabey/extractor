import os
from collections import defaultdict
import datetime as dt
from timeit import default_timer as timer

import flask
from flask import request, render_template
from flask_login import login_required, login_user, logout_user

from sqlalchemy.orm import exc

from Extractor import app, login_manager
from Extractor.utils import parse_csv_csv, parse_csv_pandas, date_parser, is_safe_url
from Extractor.database import db_session
from Extractor.models import User, Dataset, Variable, UserToken
from Extractor.forms import LoginForm, DatasetForm


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, hint='', status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.hint = hint
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(400)
def page_not_found(e):
    print(e)
    return render_template('400.html'), 400

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = flask.make_response(render_template('invalid_usage.html', error=error))
    response.status_code = error.status_code
    return response

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data_extractor')
def data_extractor():
    datasets = Dataset.query.all()
    return render_template('data_extractor.html', datasets=datasets)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()

    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class

        user = User.query.filter_by(name=form.name.data).one()
        if not user.check_password(form.password.data):
            return flask.abort(400)
        login_user(user)

        flask.flash('Logged in successfully.')

        next_page = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next_page):
            return flask.abort(400)

        return flask.redirect(next_page or flask.url_for('index'))
    return flask.render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect('/')


@app.route('/dataset/create', methods=['GET', 'POST'])
@login_required
def create_dataset():
    form = DatasetForm()
    if form.validate_on_submit():
        ds = Dataset(form.label.data, form.label.data, 
                     dt.datetime(2017, 1, 1), dt.datetime.now(),
                     5, form.label.data, form.instrument.data, 
                     '/some/file/path/{year}/', 
                     'TimeStamp' , '%d%m', 'Time', '%s')
        db_session.add(ds)
        db_session.commit()

        return flask.redirect(flask.url_for('datasets'))
    return render_template('edit_dataset.html', form=form)
    

@app.route('/dataset/<dataset_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_dataset(dataset_name):
    ds = Dataset.query.filter_by(name=dataset_name).one()
    form = DatasetForm(obj=ds)

    if form.validate_on_submit():
        form.populate_obj(ds)
        db_session.commit()

        return flask.redirect(flask.url_for('datasets'))
    return render_template('edit_dataset.html', form=form)
    

@app.route('/dataset/<dataset_name>/vars.json')
def get_dataset_vars(dataset_name):
    ds = Dataset.query.filter_by(name=dataset_name).one()
    variables = defaultdict(list)
    for var in ds.variables:
        variables[var.vartype].append({'var': var.var,
                                       'long_name': var.long_name,
                                        'units': var.units})

    return flask.jsonify(variables)

@app.route('/dataset/<dataset_name>/delete', methods=['POST'])
@login_required
def delete_dataset(dataset_name):
    print(request.method)
    ds = Dataset.query.filter_by(name=dataset_name).one()
    db_session.delete(ds)
    db_session.commit()

    return flask.redirect(flask.url_for('datasets'))
    

@app.route('/datasets')
def datasets():
    datasets = Dataset.query.all()
    return render_template('datasets.html', datasets=datasets)
    

@app.route('/datasets.json')
def datasets_json():
    datasets = Dataset.query.all()
    return flask.jsonify(datasets=[ds.name for ds in datasets])

    

@app.route('/dataset/<dataset_name>/')
def dataset(dataset_name):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    return render_template('dataset.html', dataset=dataset)

    
@app.route('/dataset/<dataset_name>.json')
def dataset_json(dataset_name):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    dataset_dict = {'name': dataset.name,
                    'instrument': dataset.instrument,
                    'variables': [{'var': v.var, 'long_name': v.long_name} for v in dataset.variables]}
    return flask.jsonify(dataset=dataset_dict)
    

@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)
    

@app.route('/user_tokens')
@login_required
def user_tokens():
    user_tokens = UserToken.query.all()
    return render_template('user_tokens.html', user_tokens=user_tokens)
    

@app.route('/user_token/create', methods=['POST'])
@login_required
def create_token():
    import uuid
    token = UserToken(uuid.uuid4().hex[:10], dt.datetime.now(), '')
    db_session.add(token)
    db_session.commit()
    return flask.redirect(flask.url_for('user_tokens'))
    


@app.route('/user_token/<token_id>/delete', methods=['POST'])
@login_required
def delete_token(token_id):
    token = UserToken.query.get(token_id)
    db_session.delete(token)
    db_session.commit()
    return flask.redirect(flask.url_for('user_tokens'))


@app.route('/dataset/<dataset_name>/get_data')
def get_data(dataset_name):
    start = timer()
    try:
        ds = Dataset.query.filter_by(name=dataset_name).one()
    except exc.NoResultFound:
        datasets = [d[0] for d in Dataset.query.with_entities(Dataset.name).all()]
        print(datasets)
        raise InvalidUsage('Dataset {} does not exist'.format(dataset_name),
                           'Available datasets are:w {}'.format(', '.join(datasets)),
                           404)

    data_format = request.args.get('data_format', 'json')
    token_str = request.args.get('token', 'none')
    if token_str != 'none':
        try:
            token = UserToken.query.filter_by(token=token_str).one()
        except exc.NoResultFound:
            raise InvalidUsage('Token {} not found'.format(token_str))
    else:
        token = None
    parser = request.args.get('parser', 'csv')

    variables = request.args.getlist('var')
    if not variables:
        raise InvalidUsage('No variables selected')

    now = dt.datetime.now()
    start_date_ts = request.args.get('start_date')
    start_date = date_parser(start_date_ts, fmt='%Y-%m-%d-%H:%M:%S')
    if not start_date_ts or not start_date:
        now_formatted = now.strftime('%Y-%m-%d-%H:%M:%S')
        raise InvalidUsage('Please enter a valid start date in form: %Y-%m-%d-%H:%M:%S',
                           'e.g. {} for now'.format(now_formatted))

    end_date_ts = request.args.get('end_date')
    end_date = date_parser(end_date_ts, fmt='%Y-%m-%d-%H:%M:%S')
    if not end_date_ts or not end_date:
        now_formatted = now.strftime('%Y-%m-%d-%H:%M:%S')
        raise InvalidUsage('Please enter a valid end date in form: %Y-%m-%d-%H:%M:%S',
                           'e.g. {} for now'.format(now_formatted))

    if start_date > now or end_date > now:
        raise InvalidUsage('Both start and end date must be before now')

    if False and not token and (end_date - start_date > dt.timedelta(hours=6)):
        return 'No token supplied and more than 6 hours of data requested'

    file_date = dt.datetime(start_date.year, start_date.month, start_date.day)
    rows = []
    while file_date < end_date:
        file_date_tuple = file_date.timetuple()

        fmt_dict = {'year': file_date.year,
                    'month': str(file_date.month).zfill(2),
                    'day': str(file_date.day).zfill(2),
                    'yday': str(file_date_tuple.tm_yday).zfill(3)}

        csv_file = ds.file_pattern.format(**fmt_dict)
        if not os.path.exists(csv_file):
            return 'uh-oh'
            raise Exception('Path {} does not exist'.format(csv_file))

        cols, units, curr_rows = parse_csv_csv(csv_file, variables, start_date, end_date)
        rows.extend(curr_rows)
        file_date += dt.timedelta(days=1)

    if data_format == 'html':
        html_rows = ['<table border="1">']

        header_row = []
        header_row.append('<thead><tr>')
        for col in cols:
            header_row.append('<th>{}</th>'.format(col))
        header_row.append('</tr></thead>')
        html_rows.append(''.join(header_row))

        html_rows.append('<tbody>')
        for row in rows:
            html_row = []
            html_row.append('<tr>')
            for cell in row:
                html_row.append('<td>{}</td>'.format(cell))
            html_row.append('</tr>')
            html_rows.append(''.join(html_row))
        html_rows.append('</tbody>')
        html_rows.append('</table>')

        payload = '\n'.join(html_rows)

    elif data_format == 'json':
        json_rows = ['{"header": [']

        header_row = []
        for col in cols:
            header_row.append('"{}"'.format(col))
        json_rows.append(','.join(header_row))
        json_rows.append('], "data": [')

        json_data_rows = []
        for row in rows:
            json_row = []
            for cell in row:
                json_row.append('"{}"'.format(cell))
            json_data_rows.append('[' + ','.join(json_row) + ']')
        json_rows.append(','.join(json_data_rows))
        json_rows.append(']}')
        payload = ''.join(json_rows)

    parsed = timer()
    print(parsed - start)

    return payload
