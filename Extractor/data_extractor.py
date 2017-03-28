import os
import datetime as dt
from timeit import default_timer as timer

from sqlalchemy.orm import exc

from Extractor.utils import parse_csv, date_parser, DATE_FMT
from Extractor.models import Dataset, UserToken
from Extractor.exceptions import InvalidUsage, MaxRowsExceeded


class DataExtractor(object):
    def __init__(self, dataset_name, request):
        self.dataset_name = dataset_name
        self.request = request
        self.curr_csv_file = None

    def __repr__(self):
        return '<DataExtractor {}>'.format(self.dataset_name)

    def __str__(self):
        return '<DataExtractor {}>'.format(self.dataset_name)

    def load(self):
        # Load the requested dataset.
        try:
            self.dataset = Dataset.query.filter_by(name=self.dataset_name).one()
        except exc.NoResultFound:
            datasets = [d[0] for d in Dataset.query.with_entities(Dataset.name).all()]
            raise InvalidUsage('Dataset {} does not exist'.format(self.dataset_name),
                               'Available datasets are:w {}'.format(', '.join(datasets)),
                               404)

    def validate(self):
        """Validate all request arguments. Save variables to self."""
        request = self.request
        data_format = request.args.get('data_format', 'json')
        if data_format not in ['html', 'json']:
            raise InvalidUsage('Unknown data format: {}'.format(data_format),
                               'Choices are html, json')

        now = dt.datetime.now()
        start_date_ts = request.args.get('start_date')
        start_date = date_parser(start_date_ts, fmt=DATE_FMT)
        if not start_date_ts or not start_date:
            now_formatted = now.strftime(DATE_FMT)
            raise InvalidUsage('Please enter a valid start date in form: {}'.format(DATE_FMT),
                               'e.g. {} for now'.format(now_formatted))

        end_date_ts = request.args.get('end_date')
        end_date = date_parser(end_date_ts, fmt=DATE_FMT)
        if not end_date_ts or not end_date:
            now_formatted = now.strftime(DATE_FMT)
            raise InvalidUsage('Please enter a valid end date in form: {}'.format(DATE_FMT),
                               'e.g. {} for now'.format(now_formatted))

        if start_date > now or end_date > now:
            raise InvalidUsage('Both start and end date must be before now')

        if start_date > end_date:
            raise InvalidUsage('Start date must be before end date')

        if False and not token and (end_date - start_date > dt.timedelta(hours=6)):
            return 'No token supplied and more than 6 hours of data requested'

        token_str = request.args.get('token', 'none')
        if token_str != 'none':
            try:
                token = UserToken.query.filter_by(token=token_str).one()
                if now > token.expiry_date:
                    raise InvalidUsage('Token {} has expired'.format(token_str))
                
                if self.dataset not in token.datasets:
                    raise InvalidUsage('Token does not give access to {}'.format(self.dataset.name))

                if (end_date - start_date).total_seconds() / 3600. > token.max_request_time_hours:
                    raise InvalidUsage('Token does only gives access to {} hour(s) of data'.format(token.max_request_time_hours))

            except exc.NoResultFound:
                raise InvalidUsage('Token {} not found'.format(token_str))
        else:
            raise InvalidUsage('Token must be supplied')

        variables = request.args.getlist('var')
        if not variables:
            raise InvalidUsage('No variables selected')
        
        missing = request.args.get('missing', 'blank')
        if missing == 'blank':
            missing_val = ''
        else:
            if missing not in ['9999.9', 'x']:
                try:
                    missing_val = float(missing)
                except ValueError:
                    raise InvalidUsage('missing value {} not recognized'.format(missing))
            else:
                missing_val = missing
        
        varnames = dict([(v.var, v.long_name) for v in self.dataset.variables])
        for variable in variables:
            if variable not in varnames:
                raise InvalidUsage('Variable not recognized: {}'.format(variable))

        self._set(start_date, end_date, variables, token, data_format, missing_val)

    def run(self, stream=False):
        timer_start = timer()

        self.generate_filelist()

        for line in self.extract_data_stream():
            yield line
    
    def _set(self, start_date, end_date, variables, token=None, data_format='json', missing_val=None):
        self.start_date = start_date
        self.end_date = end_date
        self.variables = variables
        self.token = token
        self.data_format = data_format
        self.missing_val = missing_val

        if self.token:
            self.max_request_rows = token.max_request_rows
            self.max_request_files = token.max_request_files
        else:
            self.max_request_rows = 1000000
            self.max_request_files = 50

    def generate_filelist(self):
        """Generate list of CSV files to get data from. Complain if any file doesn't exist."""
        start_date = self.start_date
        end_date = self.end_date
        file_date = dt.datetime(start_date.year, start_date.month, start_date.day)
        csv_files = []
        while file_date < end_date:
            file_date_tuple = file_date.timetuple()

            fmt_dict = {'year': file_date.year,
                        'month': str(file_date.month).zfill(2),
                        'day': str(file_date.day).zfill(2),
                        'yday': str(file_date_tuple.tm_yday).zfill(3)}

            csv_file = self.dataset.file_fmt.format(**fmt_dict)
            if not os.path.exists(csv_file):
                raise InvalidUsage('Path {} does not exist'.format(csv_file))
            csv_files.append(csv_file)
            file_date += dt.timedelta(days=1)

        self.csv_files = csv_files

        if len(self.csv_files) > self.max_request_files:
            raise InvalidUsage('Token does only gives access to {} file(s)'.format(self.max_request_files))


    def extract_data(self):
        """Parse all CSV files sequentially, storing results"""
        # Parse files. 
        self.rows = []
        for csv_file in self.csv_files:
            curr_rows = len(self.rows)
            max_rows = self.max_request_rows - curr_rows
            self.curr_csv_file = csv_file
            # TODO: May be able to get units from one file but not another.
            # TODO: Get if possible (don't just take last).
            try:
                self.cols, self.units, curr_rows = parse_csv(csv_file, 
                                                             self.variables, 
                                                             self.start_date, 
                                                             self.end_date,
                                                             self.dataset.date_col_name,
                                                             self.dataset.time_col_name,
                                                             self.dataset.datetime_fmt,
                                                             max_rows)
            except MaxRowsExceeded as mre:
                raise InvalidUsage('Token only allows access to {} rows'.format(self.max_request_rows))
            self.rows.extend(curr_rows)

    def extract_data_stream(self):
        """Parse all CSV files sequentially, storing results"""

        written_header = False
        # Parse files. 
        for i, csv_file in enumerate(self.csv_files):
            self.curr_csv_file = csv_file
            max_rows = 1e6

            # TODO: May be able to get units from one file but not another.
            # TODO: Get if possible (don't just take last).
            try:
                self.cols, self.units, curr_rows = parse_csv(csv_file, 
                                                             self.variables, 
                                                             self.start_date, 
                                                             self.end_date,
                                                             self.dataset.date_col_name,
                                                             self.dataset.time_col_name,
                                                             self.dataset.datetime_fmt,
                                                             max_rows)
                if not written_header:
                    for header_line in self.format_header_json(self.cols):
                        yield header_line
                    written_header = True
                
                if i == len(self.csv_files) - 1:
                    last = True
                else:
                    last = False
                for data_row in self.format_data_json(curr_rows, last):
                    yield data_row

            except MaxRowsExceeded as mre:
                raise InvalidUsage('Token only allows access to {} rows'.format(self.max_request_rows))

        yield self.format_footer_json()

    def format_header_json(self, cols):
        json_rows = ['{"header": [']

        header_row = []
        for col in cols:
            header_row.append('"{}"'.format(col))
        json_rows.append(','.join(header_row))
        json_rows.append('], "data": [')
        return json_rows

    def format_data_json(self, rows, last):
        def format_row(row):
            json_row = []
            for cell in row:
                if cell is None:
                    json_row.append('"{}"'.format(self.missing_val))
                else:
                    json_row.append('"{}"'.format(cell))
            return '[' + ','.join(json_row) + '],'

        print(len(rows))
        for row in rows[:-1]:
            yield format_row(row)

        if last:
            yield format_row(rows[-1])[:-1]
        else:
            yield format_row(rows[-1])

    def format_footer_json(self):
        return ']}'


    def format_response(self):
        cols, units, rows = self.cols, self.units, self.rows
        # Format response.
        if self.data_format == 'html':
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
                    if cell is None:
                        html_row.append('<td>{}</td>'.format(self.missing_val))
                    else:
                        html_row.append('<td>{}</td>'.format(cell))
                html_row.append('</tr>')
                html_rows.append(''.join(html_row))
            html_rows.append('</tbody>')
            html_rows.append('</table>')

            payload = '\n'.join(html_rows)

        elif self.data_format == 'json':
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
                    if cell is None:
                        json_row.append('"{}"'.format(self.missing_val))
                    else:
                        json_row.append('"{}"'.format(cell))
                json_data_rows.append('[' + ','.join(json_row) + ']')
            json_rows.append(','.join(json_data_rows))
            json_rows.append(']}')
            payload = ''.join(json_rows)

        return payload
