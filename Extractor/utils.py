import datetime as dt

from urlparse import urlparse, urljoin
from flask import request, url_for

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def date_parser(timestamp, fmt='%d/%m/%Y %H:%M:%S'):
    try:
        return dt.datetime.strptime(timestamp, fmt)
    except (ValueError, TypeError):
        return None


def parse_csv_pandas(csv_file, variables, start_date, end_date):
    import numpy as np
    import pandas as pd

    try:
        df = pd.read_csv(csv_file, skiprows=[1], parse_dates=[0], date_parser=date_parser)
        for var in variables:
            if var not in df.columns:
                msg_fmt = 'Field {} not recognized, please pick from {}'
                raise Exception(msg_fmt.format(var, ', '.join(df.columns)))
        df_requested = df[variables]
    except Exception as e:
        return str(e)

    return df_requested.loc[(df['TimeStamp'] >= start_date) & 
                            (df['TimeStamp'] <= end_date)]


def parse_csv_csv(csv_file, variables, start_date, end_date):
    import csv

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = reader.next()
        all_units = reader.next()

        col_indices = []
        try:
            if 'TimeStamp' in header and 'Time' in header:
                date_index = header.index('TimeStamp')
                time_index = header.index('Time')
                split_time = True
            else:
                datetime_index = header.index('TimeStamp')
                split_time = False

            for var in variables:
                col_indices.append(header.index(var))
        except ValueError as e:
            return ', '.join(header)

        cols = ['TimeStamp']
        units = ['timestamp']
        for i in col_indices:
            cols.append(header[i])
            units.append(all_units[i])

        rows = []

        for csv_row in reader:
            row = []
            if split_time:
                time = csv_row[time_index]
                if time[:2] == '24':
                    time = '00' + time[2:]
                    add_time = dt.timedelta(days=1)
                else:
                    add_time = dt.timedelta(days=0)
                timestamp = '{} {}'.format(csv_row[date_index], time)
                row_time = date_parser(timestamp, '%Y%m%d %H%M') + add_time
            else:
                timestamp = csv_row[datetime_index]
                row_time = date_parser(timestamp)

            if row_time > end_date:
                break
            if row_time >= start_date:
                row.append(str(row_time))
                for i in col_indices:
                    row.append(csv_row[i])
                rows.append(row)

        return cols, units, rows
