import datetime as dt


def date_parser(timestamp, fmt='%d/%m/%Y %H:%M:%S'):
    return dt.datetime.strptime(timestamp, fmt)


def parse_csv_pandas(csv_file, fields, start_date, end_date, data_format):
    import numpy as np
    import pandas as pd

    try:
        df = pd.read_csv(csv_file, skiprows=[1], parse_dates=[0], date_parser=date_parser)
        for field in fields:
            if field not in df.columns:
                msg_fmt = 'Field {} not recognized, please pick from {}'
                raise Exception(msg_fmt.format(field, ', '.join(df.columns)))
        df_requested = df[fields]
    except Exception as e:
        return str(e)

    if data_format == 'json':
        return df_requested.loc[(df['TimeStamp'] >= start_date) & 
                                (df['TimeStamp'] <= end_date)].to_json()
    elif data_format == 'html':
        return df_requested.loc[(df['TimeStamp'] >= start_date) & 
                                (df['TimeStamp'] <= end_date)].to_html()


def parse_csv_csv(csv_file, fields, start_date, end_date, data_format):
    import csv

    with open(csv_file, 'r') as f:
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
