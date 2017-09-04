import csv
import datetime as dt
from urlparse import urlparse, urljoin

from flask import request

from Extractor.exceptions import MaxRowsExceeded
import tempfile
import os
import uuid
import shutil
DATE_FMT = '%Y-%m-%d-%H:%M:%S'

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def date_parser(timestamp, fmt):
    try:
        return dt.datetime.strptime(timestamp, fmt)
    except (ValueError, TypeError):
        print('(timestamp, fmt): ({}, {})'.format(timestamp, fmt))
        for midnight24, midnight00 in [('2400', '0000'),
                                       ('24:00:00', '00:00:00')]:
            if midnight24 in timestamp:
                return dt.datetime.strptime(timestamp.replace(midnight24, midnight00), fmt) + dt.timedelta(days=1)
        raise


def parse_csv(csv_file, variables, start_date, end_date, date_col_name, time_col_name, datetime_fmt, max_rows):
    tfname = os.path.join(tempfile.gettempdir(), 'UoR_extractor_' + str(uuid.uuid4()) + '.csv')

    try:
        # Copy to temporary file and read from there
        # (reduce charged disk transactions and /tmp is SSD on Azure F1 machines so less latency)
        shutil.copy(csv_file, tfname)
        csv_file = tfname
    except Exception,e:
        pass # Just use the original CSV file if a problem

    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            header = reader.next()
            all_units = reader.next()

            col_data = []
            if time_col_name != '':
                split_datetime = True
            else:
                split_datetime = False

            if split_datetime:
                date_index = header.index(date_col_name)
                time_index = header.index(time_col_name)
            else:
                datetime_index = header.index(date_col_name)

            for var in variables:
                if var in header:
                    col_data.append((header.index(var), var))
                else:
                    col_data.append((None, var))

            cols = ['TimeStamp']
            units = ['timestamp']
            for cd in col_data:
                if cd[0] is not None:
                    cols.append(header[cd[0]])
                    units.append(all_units[cd[0]])
                else:
                    cols.append(cd[1])
                    units.append('-')

            rows = []

            for csv_row in reader:
                row = []
                if split_datetime:
                    timestamp = '{} {}'.format(csv_row[date_index], csv_row[time_index])
                else:
                    timestamp = csv_row[datetime_index]

                row_time = date_parser(timestamp, datetime_fmt)

                if row_time > end_date:
                    break
                if row_time >= start_date:
                    row.append(str(row_time))
                    for cd in col_data:
                        if cd[0] is not None:
                            try:
                                val = float(csv_row[cd[0]])
                                row.append(val)
                            except ValueError:
                                row.append(None)
                        else:
                            row.append(None)
                    rows.append(row)
                    if len(rows) > max_rows:
                        raise MaxRowsExceeded(len(rows))

            return cols, units, rows
    except Exception, e:
        raise e
    finally:
        # Always remove the temp file when finished
        try:
            os.remove(tfname)
        except:
            pass