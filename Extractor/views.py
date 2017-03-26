import os
from collections import defaultdict
import datetime as dt
import uuid

import flask
from flask import request, render_template
from flask_login import login_required, login_user, logout_user

from Extractor import app, login_manager
from Extractor.utils import parse_csv, is_safe_url
from Extractor.database import db_session
from Extractor.models import User, Dataset, Variable, UserToken
from Extractor.forms import LoginForm, DatasetForm, VariableForm, TokenForm
from Extractor.data_extractor import DataExtractor
from Extractor.exceptions import InvalidUsage


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
        existing_dataset = Dataset.query.filter_by(name=form.name.data).one_or_none()
        if existing_dataset is not None:
            raise InvalidUsage('Dataset {} already exists'.format(form.name.data))

        dataset = Dataset(None, None, None, None, None, None, None, None, None) 
        form.populate_obj(dataset)

        db_session.add(dataset)
        db_session.commit()

        return flask.redirect(flask.url_for('datasets'))
    return render_template('edit_dataset.html', form=form)
    

@app.route('/dataset/<dataset_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_dataset(dataset_name):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    form = DatasetForm(obj=dataset)

    if form.validate_on_submit():
        form.populate_obj(dataset)
        db_session.commit()

        return flask.redirect(flask.url_for('datasets'))
    return render_template('edit_dataset.html', form=form)
    

@app.route('/dataset/<dataset_name>/var/create', methods=['GET', 'POST'])
@login_required
def create_var(dataset_name):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    form = VariableForm()

    if form.validate_on_submit():
        existing_variable = Variable.query.filter_by(var=form.var.data).one_or_none()
        if existing_variable is not None:
            raise InvalidUsage('Variable {} already exists'.format(form.var.data))
        variable = Variable('', '', '', '')
        form.populate_obj(variable)
        dataset.variables.append(variable)
        db_session.add(variable)
        db_session.commit()

        return flask.redirect(flask.url_for('get_dataset_vars', dataset_name=dataset.name))
    return render_template('edit_var.html', form=form)


@app.route('/dataset/<dataset_name>/<var_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_var(dataset_name, var_name):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    var = dataset.variables.filter_by(var=var_name).one()
    form = VariableForm(obj=var)

    if form.validate_on_submit():
        form.populate_obj(var)
        db_session.commit()

        return flask.redirect(flask.url_for('get_dataset_vars', dataset_name=dataset.name))
    return render_template('edit_var.html', form=form)
    
@app.route('/dataset/<dataset_name>/<var_id>/delete', methods=['POST'])
@login_required
def delete_var(dataset_name, var_id):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    var = Variable.query.filter_by(dataset=dataset, id=var_id).one()
    db_session.delete(var)
    db_session.commit()

    return flask.redirect(flask.url_for('get_dataset_vars', dataset_name=dataset.name))
    

@app.route('/dataset/<dataset_name>/vars')
def get_dataset_vars(dataset_name):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    return render_template('vars.html', dataset=dataset)

@app.route('/dataset/<dataset_name>/vars.json')
def get_dataset_vars_json(dataset_name):
    dataset = Dataset.query.filter_by(name=dataset_name).one()
    variables = defaultdict(list)
    for var in dataset.variables:
        variables[var.vartype].append({'var': var.var,
                                       'long_name': var.long_name,
                                        'units': var.units})

    return flask.jsonify(variables)

@app.route('/dataset/<dataset_id>/delete', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
    print(request.method)
    dataset = Dataset.query.get(dataset_id)
    db_session.delete(dataset)
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
                    'long_name': dataset.long_name,
                    'start_date': dataset.start_date.strftime(DATE_FMT),
                    'end_date': dataset.end_date.strftime(DATE_FMT),
                    'variables': [{'var': v.var, 'long_name': v.long_name, 'units': v.units, 'vartype': v.vartype} for v in dataset.variables]}
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
    

@app.route('/user_token/create', methods=['GET', 'POST'])
@login_required
def create_token():
    if request.method == 'GET':
        dummy_token = UserToken(uuid.uuid4().hex[:10], dt.datetime.now() + dt.timedelta(days=5))
        form = TokenForm(obj=dummy_token)
    else:
        new_token = UserToken('', '', '', )
        form = TokenForm()
    form.dataset_ids.choices = [(ds.id, ds.name) for ds in Dataset.query.all()]

    if form.validate_on_submit():
        existing_token = UserToken.query.filter_by(token=form.token.data).one_or_none()
        if existing_token is not None:
            raise InvalidUsage('Token {} already exists'.format(form.token.data))
        form.populate_obj(new_token)
        for dataset_id in form.dataset_ids.data:
            dataset = Dataset.query.get(dataset_id)
            new_token.datasets.append(dataset)
        db_session.add(new_token)
        db_session.commit()

        return flask.redirect(flask.url_for('user_tokens'))
    return render_template('edit_token.html', form=form)


@app.route('/user_token/<token_id>/delete', methods=['POST'])
@login_required
def delete_token(token_id):
    token = UserToken.query.get(token_id)
    db_session.delete(token)
    db_session.commit()
    return flask.redirect(flask.url_for('user_tokens'))


@app.route('/dataset/<dataset_name>/get_data')
def get_data(dataset_name):
    try:
        extractor = DataExtractor(dataset_name, request)
        extractor.load()
        extractor.validate()
        return extractor.run()
    except Exception as e:
        # Pokemon exception handling!
        hint = ''
        if extractor.curr_csv_file:
            hint += 'Current CSV file: {}\n'.format(extractor.curr_csv_file)
        raise InvalidUsage(e.message, hint)
