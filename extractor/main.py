import os
import datetime as dt
from timeit import default_timer as timer

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from datasets import DATASETS

# Create flask object and configure based on site specific host_config.txt
app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
config = open(os.path.join(dir_path, 'host_config.txt'), 'r').read().strip()
app.config.from_object(config)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(dir_path, 'extractor.db'))
db = SQLAlchemy(app)


class DataSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<DataSet {} (id={})>'.format(self.name, self.id)


def date_parser(timestamp, fmt='%d/%m/%Y %H:%M:%S'):
    return dt.datetime.strptime(timestamp, fmt)


@app.route('/')
def index():
    #ds = DataSet.query.first()
    #datasets = DataSet.query.all()
    return render_template('index.html', datasets=DATASETS)


@app.route('/login')
def login():
    return render_template('login.html')


def parse_csv_pandas(fields, start_date, end_date, data_format):
    import numpy as np
    import pandas as pd

    try:
        df = pd.read_csv(os.path.join(app.config['DATA_LOCATION'], '2015-SMP1-086.csv'), 
                         skiprows=[1], parse_dates=[0], date_parser=date_parser)
        for field in fields:
            if field not in df.columns:
                msg = 'Field {} not recognized, please pick from {}'.format(field, 
                                                                            ', '.join(df.columns))
                raise Exception(msg)
        df_requested = df[fields]
    except Exception as e:
        return str(e)

    if data_format == 'json':
        return df_requested.loc[(df['TimeStamp'] >= start_date) & (df['TimeStamp'] <= end_date)].to_json()
    elif data_format == 'html':
        return df_requested.loc[(df['TimeStamp'] >= start_date) & (df['TimeStamp'] <= end_date)].to_html()


def parse_csv_csv(fields, start_date, end_date, data_format):
    import csv

    with open(os.path.join(app.config['DATA_LOCATION'], '2015-SMP1-086.csv'), 'r') as f:
        reader = csv.reader(f)
        cols = reader.next()
        units = reader.next()

        col_indices = []
        try:
            time_index = cols.index('TimeStamp')
            for field in fields:
                col_indices.append(cols.index(field))
        except ValueError as e:
            return ', '.join(cols)

        if data_format == 'html':
            rows = ['<table border="1">']

            row = []
            row.append('<thead><tr>')
            row.append('<th>Time</th>')
            for i in col_indices:
                row.append('<th>{}</th>'.format(cols[i]))
            row.append('</tr></thead>')
            rows.append(''.join(row))

            row.append('<tbody>')
            for csv_row in reader:
                row = []
                row_time = date_parser(csv_row[time_index])
                if row_time > end_date:
                    break
                if row_time >= start_date:
                    row.append('<tr>')
                    row.append('<td>{}</td>'.format(str(row_time)))
                    for i in col_indices:
                        row.append('<td>{}</td>'.format(csv_row[i]))
                    row.append('</tr>')
                    rows.append(''.join(row))
            row.append('</tbody>')
            rows.append('</table>')

            return '\n'.join(rows)
        elif data_format == 'json':
            rows = ['{"header": [']

            row = []
            row.append('"Time"')
            for i in col_indices:
                row.append('"{}"'.format(cols[i]))
            rows.append(','.join(row))
            rows.append('], "data": [')

            data_rows = []
            for csv_row in reader:
                row = []
                row_time = date_parser(csv_row[time_index])
                if row_time > end_date:
                    break
                if row_time >= start_date:
                    row.append('"{}"'.format(str(row_time)))
                    for i in col_indices:
                        row.append('"{}"'.format(csv_row[i]))
                    data_rows.append('[' + ','.join(row) + ']')
            rows.append(','.join(data_rows))
            rows.append(']}')

            return ''.join(rows)



@app.route('/get_data')
def get_data():
    start = timer()
    data_format = request.args.get('data_format', 'json')
    parser = request.args.get('parser', 'csv')

    fields = request.args.getlist('field')
    start_date_ts = request.args.get('start_date')
    end_date_ts = request.args.get('end_date')
    start_date = date_parser(start_date_ts, fmt='%Y-%m-%d-%H:%M:%S')
    end_date = date_parser(end_date_ts, fmt='%Y-%m-%d-%H:%M:%S')

    if parser == 'pandas':
        payload =  parse_csv_pandas(fields, start_date, end_date, data_format)
    elif parser == 'csv':
        payload =  parse_csv_csv(fields, start_date, end_date, data_format)

    parsed = timer()
    print(parsed - start)

    return payload

if __name__ == '__main__':
    app.run()
