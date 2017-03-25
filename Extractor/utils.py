import datetime as dt
import csv

from urlparse import urlparse, urljoin
from flask import request, url_for

from Extractor.exceptions import InvalidUsage


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


def parse_csv(csv_file, variables, start_date, end_date, date_fmt='%Y%m%d %H%M'):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = reader.next()
        all_units = reader.next()

        col_data = []
        if 'TimeStamp' in header:
            if 'Time' in header:
                date_index = header.index('TimeStamp')
                time_index = header.index('Time')
                split_time = True
            elif 'hhmm' in header:
                date_index = header.index('TimeStamp')
                time_index = header.index('hhmm')
                split_time = True
            else:
                datetime_index = header.index('TimeStamp')
                split_time = False
        elif 'Date' in header and 'Time' in header:
            date_index = header.index('Date')
            time_index = header.index('Time')
            split_time = True

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
            if split_time:
                time = csv_row[time_index]
                if time[:2] == '24':
                    time = '00' + time[2:]
                    add_time = dt.timedelta(days=1)
                else:
                    add_time = dt.timedelta(days=0)
                timestamp = '{} {}'.format(csv_row[date_index], time)
                row_time = date_parser(timestamp, date_fmt) + add_time
            else:
                timestamp = csv_row[datetime_index]
                row_time = date_parser(timestamp, date_fmt)

            if row_time is None:
                raise InvalidUsage('Could not parse time: {} with: {}'.format(timestamp, date_fmt))
            # print(row_time)
            if row_time > end_date:
                break
            if row_time >= start_date:
                row.append(str(row_time))
                for cd in col_data:
                    if cd[0] is not None:
                        row.append(csv_row[cd[0]])
                    else:
                        row.append(None)
                rows.append(row)

        return cols, units, rows
