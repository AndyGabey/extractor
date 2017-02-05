import os
from timeit import default_timer as timer

from flask import request, render_template

from extractor import app
from extractor.utils import parse_csv_csv, parse_csv_pandas, date_parser
from extractor.datasets import DATASETS


@app.route('/')
def index():
    return render_template('index.html', datasets=DATASETS)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/datasets')
def datasets():
    dataset_list = []
    for k, v in DATASETS.items():
        for ds_value, ds_name in v.items():
            dataset_list.append((ds_name, ds_value))

    return render_template('datasets.html', datasets=dataset_list)
    

@app.route('/dataset/<dataset>/')
def dataset(dataset):
    for k, v in DATASETS.items():
        if dataset in v:
            return render_template('dataset.html', ds_name=v[dataset], ds_value=dataset)

    return 'Unknown dataset'
    

@app.route('/dataset/<dataset>/get_data')
def get_data(dataset):
    start = timer()
    print(dataset)
    data_format = request.args.get('data_format', 'json')
    parser = request.args.get('parser', 'csv')

    fields = request.args.getlist('field')
    start_date_ts = request.args.get('start_date')
    end_date_ts = request.args.get('end_date')
    start_date = date_parser(start_date_ts, fmt='%Y-%m-%d-%H:%M:%S')
    end_date = date_parser(end_date_ts, fmt='%Y-%m-%d-%H:%M:%S')

    csv_file = os.path.join(app.config['DATA_LOCATION'], '2015-SMP1-086.csv')

    if parser == 'pandas':
        payload =  parse_csv_pandas(csv_file, fields, start_date, end_date, data_format)
    elif parser == 'csv':
        payload =  parse_csv_csv(csv_file, fields, start_date, end_date, data_format)

    parsed = timer()
    print(parsed - start)

    return payload
