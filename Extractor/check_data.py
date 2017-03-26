import os
import re
from glob import glob
import datetime as dt
from collections import Counter, defaultdict, OrderedDict
import csv

import simplejson

from Extractor.utils import DATE_FMT

PATTERNS = {
    'metfidas': [
        # '/mnt/data/metfidas/Level1/2015/2015-AVG5-104.csv'
        #('metfidas1',
        #    re.compile('/mnt/data/metfidas/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-AVG5-(?P<doy>\d{3}).csv'),
        #    '/mnt/data/metfidas/Level1/{year}/{year}-AVG5-{doy}.csv',
        #    'year_year2_doy'),
        # '/mnt/data/metfidas/Level1/2015/2015-SMP1-104.csv'
        #('metfidas2',
        #    re.compile('/mnt/data/metfidas/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-SMP1-(?P<doy>\d{3}).csv'),
        #    '/mnt/data/metfidas/Level1/{year}/{year2}-SMP1-{doy}.csv',
        #    'year_year2_doy'),
        # '/mnt/data/metfidas/Level1/2015/2015-MMX5-104.csv'
        #('metfidas3',
        #    re.compile('/mnt/data/metfidas/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-MMX5-(?P<doy>\d{3}).csv'),
        #    '/mnt/data/metfidas/Level1/{year}/{year2}-MMX5-{doy}.csv',
        #    'year_year2_doy'),
        # '/mnt/data/metfidas/Level2/1hour/2015/20150415_1hour.csv'
        #('metfidas4',
        #    re.compile('/mnt/data/metfidas/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour.csv'),
        #    '/mnt/data/metfidas/Level2/1hour/{year}/{date}_1hour.csv',
        #    'year_date'),
        # '/mnt/data/metfidas/Level2/1hour/2015/20150415_1hour_maxmin.csv'
        #('metfidas5',
        #    re.compile('/mnt/data/metfidas/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour_maxmin.csv'),
        #    '/mnt/data/metfidas/Level2/1hour/{year}/{date}_1hour_maxmin.csv',
        #    'year_date'),
        # '/mnt/data/metfidas/Level2/5min/2015/20150415_5min.csv',
        #('metfidas6',
        #    re.compile('/mnt/data/metfidas/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min.csv'),
        #    '/mnt/data/metfidas/Level2/5min/{year}/{date}_5min.csv',
        #    'year_date'),
        # '/mnt/data/metfidas/Level2/5min/2015/20150415_5min_maxmin.csv'
        #('metfidas7',
        #    re.compile('/mnt/data/metfidas/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min_maxmin.csv'),
        #    '/mnt/data/metfidas/Level2/5min/{year}/{date}_5min_maxmin.csv',
        #    'year_date'),
        # '/mnt/data/metfidas/Level2/profile/2015/20150819_UTprofile.csv'
        ('Vertical_profiles',
            re.compile('/mnt/data/metfidas/Level2/profile/(?P<year>\d{4})/(?P<date>\d{8})_UTprofile.csv'),
            '/mnt/data/metfidas/Level2/profile/{year}/{date}_UTprofile.csv',
            'year_date'),
    ],
    'labserver_files': [
        # '/mnt/data/labserver_files/METFiDAS/data/processed/derived/2005/2005D220.csv'
        #('ls1',
        #    re.compile('/mnt/data/labserver_files/METFiDAS/data/processed/derived/(?P<year>\d{4})/(?P<year2>\d{4})D(?P<doy>\d{3}).csv'),
        #    '/mnt/data/labserver_files/METFiDAS/data/processed/derived/{year}/{year2}D{doy}.csv',
        #    'year_year2_doy'),
        # '/mnt/data/labserver_files/METFiDAS/data/processed/measured/2005/2005M220.csv'
        #('ls2',
        #    re.compile('/mnt/data/labserver_files/METFiDAS/data/processed/measured/(?P<year>\d{4})/(?P<year2>\d{4})M(?P<doy>\d{3}).csv'),
        #    '/mnt/data/labserver_files/METFiDAS/data/processed/measured/{year}/{year2}M{doy}.csv',
        #    'year_year2_doy'),
        # '/mnt/data/labserver_files/METFiDAS-3/Level1/2014/2014-AVG5-237.csv'
        ('5min_Level1',
            re.compile('/mnt/data/labserver_files/METFiDAS-3/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-AVG5-(?P<doy>\d{3}).csv'),
            '/mnt/data/labserver_files/METFiDAS-3/Level1/{year}/{year2}-AVG5-{doy}.csv',
            'year_year2_doy'),
        # '/mnt/data/labserver_files/METFiDAS-3/Level1/2014/2014-MMX5-237.csv'
        ('5min_Level1_maxmin',
            re.compile('/mnt/data/labserver_files/METFiDAS-3/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-MMX5-(?P<doy>\d{3}).csv'),
            '/mnt/data/labserver_files/METFiDAS-3/Level1/{year}/{year2}-MMX5-{doy}.csv',
            'year_year2_doy'),
        # '/mnt/data/labserver_files/METFiDAS-3/Level1/2014/2014-SMP1-237.csv'
        ('1sec_Level1',
            re.compile('/mnt/data/labserver_files/METFiDAS-3/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-SMP1-(?P<doy>\d{3}).csv'),
            '/mnt/data/labserver_files/METFiDAS-3/Level1/{year}/{year2}-SMP1-{doy}.csv',
            'year_year2_doy'),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/2014/20140831_1hour.csv',
        ('1hour_Level2',
            re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour.csv'),
            '/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/{year}/{date}_1hour.csv',
            'year_date'),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/2014/20140831_1hour_maxmin.csv',
        ('1hour_Level2_maxmin',
            re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour_maxmin.csv'),
            '/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/{year}/{date}_1hour_maxmin.csv',
            'year_date'),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/5min/2014/20140831_5min.csv',
        ('5min_Level2',
            re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min.csv'),
            '/mnt/data/labserver_files/METFiDAS-3/Level2/5min/{year}/{date}_5min.csv',
            'year_date'),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/5min/2014/20140831_5min_maxmin.csv',
        ('5min_Level2_maxmin',
            re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min_maxmin.csv'),
            '/mnt/data/labserver_files/METFiDAS-3/Level2/5min/{year}/{date}_5min_maxmin.csv',
            'year_date'),
    ],
    'SonicLicor-Incoming': [
        # '/mnt/data/SonicLicor-Incoming/Level1/2015/2015-SMP-223.csv'
        ('soniclicor_Level1',
            re.compile('/mnt/data/SonicLicor-Incoming/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-SMP-(?P<doy>\d{3}).csv'),
            '/mnt/data/SonicLicor-Incoming/Level1/{year}/{year2}-SMP-{doy}.csv',
            'year_year2_doy'),
    ],
    'Ceilometer-Incoming': [
        # '/mnt/data/Ceilometer-Incoming/Level2/1min/2016/20160604_1min.csv'
        ('cloudbase_1min', 
            re.compile('/mnt/data/Ceilometer-Incoming/Level2/1min/(?P<year>\d{4})/(?P<date>\d{8})_1min.csv'),
            '/mnt/data/Ceilometer-Incoming/Level2/1min/{year}/{date}_1min.csv',
            'year_date'),
        # '/mnt/data/Ceilometer-Incoming/Level2/5min/2014/20140501_5min.csv'
        ('cloudbase_5min', 
            re.compile('/mnt/data/Ceilometer-Incoming/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min.csv'),
            '/mnt/data/Ceilometer-Incoming/Level2/5min/{year}/{date}_5min.csv',
            'year_date'),
    ],
    'LUMA': [
        # '/mnt/data/LUMA/RUAO/ReadingFlux_2015259.csv'
        ('eddy_cov', 
            re.compile('/mnt/data/LUMA/RUAO/ReadingFlux_(?P<date_doy>\d{7}).csv'),
            '/mnt/data/LUMA/RUAO/ReadingFlux_{date_doy}.csv',
            'date_doy'),
    ],
}


def get_paths():
    csv_filenames = 'test_data/csv_filenames.txt'
    if not os.path.exists(csv_filenames):
        raise Exception('Please run bin/find_csv_files.sh first and run from root extractor dir.')
    with open(csv_filenames, 'r') as f:
        paths = map(os.path.normpath, map(str.strip, f.readlines()))
    return paths


def check_filenames():
    paths = get_paths()

    path_counter = Counter()
    instrument_paths = defaultdict(list)

    for path in paths:
        # print((os.path.exists(path), path))
        split_path = path.split(os.sep)
        instrument = split_path[3]
        # print(split_path)
        path_counter[instrument] += 1
        instrument_paths[instrument].append(path)
    print(path_counter)
    return instrument_paths


def check_path(instrument_patterns, path):
    for name, pattern, fmt, parse_opt in instrument_patterns:
        match = re.match(pattern, path)
        if match:
            return name, pattern, fmt, parse_opt, match
    return name, None, None, None, None


def check_path_format(instrument_paths):
    pattern_matches = defaultdict(list)
    unmatched = defaultdict(list)
    for instrument, paths in instrument_paths.items():
        #print(instrument)
        instrument_patterns = PATTERNS.get(instrument)
        if not instrument_patterns:
            print('  Pattern missing for {}'.format(instrument))
            continue

        for path in paths:
            name, pattern, fmt, parse_opt, match = check_path(instrument_patterns, path)
            if not match:
                #print('  Unmatched: {}'.format(path))
                unmatched[instrument].append(path)
                continue
            pattern_matches['{}:{}'.format(instrument, name)].append((path, fmt, parse_opt, match))
        print('  Unmatched count: {}'.format(len(unmatched[instrument])))
    return pattern_matches, unmatched


def check_date_parse(pattern_matches):
    dates = {}
    for name, parse_opt_matches in pattern_matches.items():
        dates[name] = {'earliest': dt.datetime(2999, 1, 1), # Intentionally later than reasonable.
                         'latest': dt.datetime(1, 1, 1)} # ditto.
        print(name)
        for path, fmt, parse_opt, match in parse_opt_matches:
            if 'fmt' not in dates[name]:
                dates[name]['fmt'] = fmt
                dates[name]['parse_opt'] = parse_opt
            else:
                assert dates[name]['fmt'] == fmt
                assert dates[name]['parse_opt'] == parse_opt

            if parse_opt == 'year_year2_doy':
                assert len(match.group('year')) == 4
                assert len(match.group('year2')) == 4
                assert len(match.group('doy')) == 3

                if match.group('year') != match.group('year2'):
                    print('Years dont match!')
                    print(path)
                    continue
                year_start = dt.datetime(int(match.group('year')), 1, 1)
                doy = int(match.group('doy'))
                date = year_start + dt.timedelta(days=doy - 1)
            elif parse_opt == 'year_date':
                assert len(match.group('year')) == 4
                assert len(match.group('date')) == 8

                year = int(match.group('year'))
                date = dt.datetime.strptime(match.group('date'), '%Y%m%d')
                if date.year != year:
                    print('Years dont match!')
                    print(path)
                    continue
            elif parse_opt == 'date_doy':
                assert len(match.group('date_doy')) == 7

                date = dt.datetime.strptime(match.group('date_doy'), '%Y%j')
            else:
                raise Exception('Unknown parse_opt {}'.format(parse_opt))
            dates[name]['earliest'] = min(date, dates[name]['earliest'])
            dates[name]['latest'] = max(date, dates[name]['latest'])
    return dates


def check_missing(dates):
    files = defaultdict(list)
    missing = []
    for k, v in dates.items():
        print(k)
        date = v['earliest']
        end = v['latest']
        fmt = v['fmt']
        parse_opt = v['parse_opt']

        while date <= end:
            if parse_opt == 'year_year2_doy':
                filename = fmt.format(year=date.year, year2=date.year, doy=date.strftime('%j'))
            elif parse_opt == 'year_date':
                filename = fmt.format(year=date.year, date=date.strftime('%Y%m%d'))
            elif parse_opt == 'date_doy':
                filename = fmt.format(date_doy=date.strftime('%Y%j'))
            else:
                raise Exception('Unknown parse_opt {}'.format(parse_opt))

            #print(filename)
            if not os.path.exists(filename):
                print('  MISSING DATE: {}'.format(date))
                print('  FILENAME: {}'.format(filename))
                missing.append(filename)
            else:
                files[k].append(filename)

            date += dt.timedelta(days=1)

    return files, missing

def parse_header(files):
    counters = {}
    for k, filenames in files.items():
        print(k)
        counter = Counter()
        for csv_file in filenames:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                header = reader.next()
            counter[','.join(header)] += 1
            #print((csv_file, len(counter)))
        print(counter)
        counters[k] = counter
    return counters


def calc_set(counters):
    for k, counter in counters.items():
        c2 = Counter()
        c3 = Counter()
        print(k)
        cols = []
        all_cols = set()
        any_cols = set()

        for ck in counter.keys():
            s = set(ck.split(','))
            key = ','.join(sorted(s))
            c2[key] += 1 
            if not any_cols:
                any_cols = s.copy()
            cols.append(s)
            all_cols |= s
            any_cols &= s
            print('    {}: {}'.format(counter[ck], ck))
            for el in s:
                c3[el] += counter[ck]

        counts = []
        for el, val in c3.items():
            counts.append((el, val))

        for count in sorted(counts, key=lambda c: c[1], reverse=True):
            print('           {}: {}'.format(*count))
        print('  Total combined headers: {}'.format(len(all_cols)))
        print('  In every header:        {}'.format(len(any_cols)))
        print('  Unique headers: {}'.format(len(counter)))
        print('  Unique sets: {}'.format(len(c2)))


def run_all():
    ips = check_filenames()
    p, u = check_path_format(ips)
    dates = check_date_parse(p)
    print('')
    #for line in ['{0: <20}: {1:%Y-%m-%d} - {2:%Y-%m-%d}'.format(k.split(':')[1], v['earliest'], v['latest']) for k, v in dates.items()]:
        #print(line)
    for k, v in dates.items():
        dataset, start_date, end_date = (k.split(':')[1], v['earliest'], v['latest'])
        print(dataset)
        fn = glob('Extractor/import_data/??_dataset_{0}.json'.format(dataset))[0]
        print((dataset, fn))

        with open(fn, 'r') as f:
            json = simplejson.load(f)

        json['start_date_ts'] = dt.datetime.strftime(start_date, DATE_FMT)
        json['end_date_ts'] = dt.datetime.strftime(end_date, DATE_FMT)

        with open(fn, 'w') as f:
            simplejson.dump(json, f, indent=2)
