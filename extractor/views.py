import os
from collections import defaultdict
import datetime as dt
from timeit import default_timer as timer

import flask
from flask import request, render_template
from flask_login import login_required, login_user, logout_user

from extractor import app, login_manager
from extractor.utils import parse_csv_csv, parse_csv_pandas, date_parser, is_safe_url
from extractor.database import db_session
from extractor.models import User, Dataset, Variable, UserToken
from extractor.forms import LoginForm, DatasetForm


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user


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
        ds = Dataset(dt.datetime(2017, 1, 1), dt.datetime.now(),
                     5, form.name.data, form.instrument.data, 
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
    


@app.route('/dataset/<dataset>/get_data')
def get_data(dataset):
    start = timer()
    print(dataset)
    data_format = request.args.get('data_format', 'json')
    token_str = request.args.get('token', 'none')
    if token_str != 'none':
        token = UserToken.query.filter_by(token=token_str).one()
    else:
        token = None

    parser = request.args.get('parser', 'csv')

    fields = request.args.getlist('field')
    start_date_ts = request.args.get('start_date')
    end_date_ts = request.args.get('end_date')
    start_date = date_parser(start_date_ts, fmt='%Y-%m-%d-%H:%M:%S')
    end_date = date_parser(end_date_ts, fmt='%Y-%m-%d-%H:%M:%S')

    if not token and (end_date - start_date > dt.timedelta(hours=6)):
        return 'No token supplied and more than 6 hours of data requested'

    csv_file = os.path.join(app.config['DATA_LOCATION'], '2015-SMP1-086.csv')

    if parser == 'pandas':
        payload =  parse_csv_pandas(csv_file, fields, start_date, end_date, data_format)
    elif parser == 'csv':
        payload =  parse_csv_csv(csv_file, fields, start_date, end_date, data_format)

    parsed = timer()
    print(parsed - start)

    return payload
