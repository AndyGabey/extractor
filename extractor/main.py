import os
import datetime as dt

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

import numpy as np
import pandas as pd

# Create flask object and configure based on site specific host_config.txt
app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
config = open(os.path.join(dir_path, 'host_config.txt'), 'r').read().strip()
app.config.from_object(config)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
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
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/get_data')
def get_data():
    data_format = request.args.get('data_format', 'json')

    fields = request.args.getlist('field')
    start_date_ts = request.args.get('start_date')
    end_date_ts = request.args.get('end_date')
    start_date = date_parser(start_date_ts, fmt='%Y-%m-%d-%H:%M:%S')
    end_date = date_parser(end_date_ts, fmt='%Y-%m-%d-%H:%M:%S')

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
        return df_requested.loc[(df['TimeStamp'] > start_date) & (df['TimeStamp'] < end_date)].to_json()
    elif data_format == 'html':
        return df_requested.loc[(df['TimeStamp'] > start_date) & (df['TimeStamp'] < end_date)].to_html()


if __name__ == '__main__':
    app.run()
