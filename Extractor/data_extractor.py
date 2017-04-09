import os
import datetime as dt
from timeit import default_timer as timer

from sqlalchemy.orm import exc

from Extractor.utils import parse_csv, date_parser, DATE_FMT
from Extractor.models import Dataset, UserToken
from Extractor.exceptions import InvalidUsage, MaxRowsExceeded
from Extractor.formatters import JsonFormatter, HtmlFormatter, CsvFormatter


class DataExtractor(object):
    def __init__(self, dataset_name, data_format, request):
        self.dataset_name = dataset_name
        self.request = request
        self.data_format = data_format

        if self.data_format == 'json':
            self.formatter = JsonFormatter()
        elif self.data_format == 'html':
            self.formatter = HtmlFormatter()
        elif self.data_format == 'csv':
            self.formatter = CsvFormatter()
        self.curr_csv_file = None
        self.dataset = None
        self.response = None
        self.csv_files = None
        self.rows = None

    def __repr__(self):
        return '<DataExtractor {}>'.format(self.dataset_name)

    def __str__(self):
        return '<DataExtractor {}>'.format(self.dataset_name)

    def error_message(self, error):
        if isinstance(error, InvalidUsage):
            return self.formatter.error_message('usage_error', error.message, error.hint)
        else:
            return self.formatter.error_message('server_error', error.message)

    def load(self):
        # Load the requested dataset.
        try:
            self.dataset = Dataset.query.filter_by(name=self.dataset_name).one()
        except exc.NoResultFound:
            datasets = [d[0] for d in Dataset.query.with_entities(Dataset.name).all()]
            raise InvalidUsage('Dataset {} does not exist'.format(self.dataset_name),
                               'Available datasets are: {}'.format(', '.join(datasets)),
                               404)

    def validate(self):
        """Validate all request arguments. Save variables to self."""
        request = self.request
        data_format = request.args.get('data_format', 'json')
        if data_format not in ['html', 'json', 'csv']:
            raise InvalidUsage('Unknown data format: {}'.format(data_format),
                               'Choices are html, json, csv')
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

        token_str = request.args.get('token', 'none')
        if token_str != 'none':
            try:
                token = UserToken.query.filter_by(token=token_str).one()
                if now > token.expiry_date:
                    raise InvalidUsage('Token {} has expired'.format(token_str))

                if self.dataset not in token.datasets:
                    raise InvalidUsage('Token does not give access to {}'.format(self.dataset.name))

                total_seconds = (end_date - start_date).total_seconds()
                if total_seconds / 3600. > token.max_request_time_hours:
                    raise InvalidUsage(
                        'Token only gives access to {} hour(s) of data'.format(token.max_request_time_hours))

                total_days = total_seconds / 86400.
                rows_requested = total_days * self.dataset.time_res
                if rows_requested > token.max_request_rows:
                    raise InvalidUsage(
                        'Token only gives access to {} row(s) of data'.format(token.max_request_rows),
                        '{} row(s) requested'.format(rows_requested))

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

    def run(self):
        timer_start = timer()
        for line in self.extract_data_stream():
            yield line
        timer_end = timer()
        print('Extracted data in {}'.format(timer_end - timer_start))
    
    def _set(self, start_date, end_date, variables, token=None, data_format='json', missing_val=None):
        self.start_date = start_date
        self.end_date = end_date
        self.variables = variables
        self.token = token
        self.formatter.missing_val = missing_val

        if self.token:
            self.max_request_rows = token.max_request_rows
            self.max_request_files = token.max_request_files
        else:
            self.max_request_rows = 1000000
            self.max_request_files = 50

    def generate_filelist(self):
        """Generate list of CSV files to get data from. Log if any file doesn't exist."""
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
                print('Path {} does not exist'.format(csv_file))
            csv_files.append(csv_file)

            if self.dataset.file_freq == 'yearly':
                # Can't set a timedelta to one year (because of leap years).
                file_date = dt.datetime(file_date.year + 1, 1, 1)
            elif self.dataset.file_freq == 'daily':
                file_date += dt.timedelta(days=1)
            else:
                raise Exception('Unknown file_freq')

        self.csv_files = csv_files

        if len(self.csv_files) > self.max_request_files:
            raise InvalidUsage('Token only gives access to {} file(s)'.format(self.max_request_files))

    def extract_data_stream(self):
        """Parse all CSV files sequentially, streaming formatted results"""
        header_sent = False
        max_rows = self.token.max_request_rows
        prev_data_row = None

        # Loop over each CSV file, parsing its contents that I care about and yielding formatted
        # output.
        for i, csv_file in enumerate(self.csv_files):
            self.curr_csv_file = csv_file

            try:
                try:
                    if not os.path.exists(csv_file):
                        # N.B. even if file does not exist, I want to print out a suitable header.
                        cols = ['TimeStamp']
                        cols.extend(self.variables)
                        units = []
                        curr_rows = []
                    else:
                        cols, units, curr_rows = parse_csv(csv_file, 
                                                           self.variables, 
                                                           self.start_date, 
                                                           self.end_date,
                                                           self.dataset.date_col_name,
                                                           self.dataset.time_col_name,
                                                           self.dataset.datetime_fmt,
                                                           max_rows)
                except Exception as parse_e:
                    raise parse_e
                    raise Exception('Parse error: {}'.format(parse_e.message))

                try:
                    if i == 0:
                        yield self.formatter.header(cols)
                        header_sent = True
                    
                    if curr_rows:
                        for data_row in self.formatter.rows(curr_rows):
                            # Convoluted? Yes a little. The problem is that it's quite hard to
                            # figure out in advance whether this is the final row or not. 
                            # Why is it hard? If you have hourly data, and a request comes in for 
                            # 21:00 - 00:30 the next day, unless you specifically check that the
                            # data is hourly, and the overlap in the next day is less than that
                            # freq, a naive algorithm for working out if it's the final row will
                            # fail. JSON will fail if there is a final comma before the list is
                            # closed, this way guarantees that only the last row will be affected.
                            # 
                            # An alternative would be to check if first, and only add a comma at the
                            # start if not first. This would require a branch on each loop tho.
                            if prev_data_row:
                                yield prev_data_row
                            prev_data_row = data_row

                except Exception as format_e:
                    raise Exception('Format error: {}'.format(format_e.message))

            except Exception as e:
                if header_sent:
                    yield self.formatter.error_footer(e.message)
                    return
                else:
                    yield self.formatter.error_message('server_error', e.message)
                    return

        if prev_data_row:
            if self.data_format == 'json':
                # See Convoluted? above for why it's done like this.
                yield prev_data_row[:-1]  # Remove final comma.
            else:
                yield prev_data_row
        yield self.formatter.footer()
