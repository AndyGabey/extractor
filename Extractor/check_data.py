import os
import re
from collections import Counter, defaultdict, OrderedDict

PATTERNS = {
    'metfidas': [
        # '/mnt/data/metfidas/Level1/2015/2015-AVG5-104.csv'
        ('metfidas1', re.compile('/mnt/data/metfidas/Level1/(?P<year>\d{4})/(?P<filename>.*).csv')),
        # '/mnt/data/metfidas/Level2/1hour/2015/20150415_1hour.csv'
        ('metfidas2', re.compile('/mnt/data/metfidas/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour.csv')),
        # '/mnt/data/metfidas/Level2/1hour/2015/20150415_1hour_maxmin.csv'
        ('metfidas3', re.compile('/mnt/data/metfidas/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour_maxmin.csv')),
        # '/mnt/data/metfidas/Level2/5min/2015/20150415_5min.csv',
        ('metfidas4', re.compile('/mnt/data/metfidas/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min.csv')),
        # '/mnt/data/metfidas/Level2/5min/2015/20150415_5min_maxmin.csv'
        ('metfidas5', re.compile('/mnt/data/metfidas/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min_maxmin.csv')),
        # '/mnt/data/metfidas/Level2/profile/2015/20150819_UTprofile.csv'
        ('metfidas6', re.compile('/mnt/data/metfidas/Level2/profile/(?P<year>\d{4})/(?P<date>\d{8})_UTprofile.csv')),
    ],
    'labserver_files': [
        # '/mnt/data/labserver_files/METFiDAS/data/processed/derived/2005/2005D220.csv'
        ('ls1', re.compile('/mnt/data/labserver_files/METFiDAS/data/processed/derived/(?P<year>\d{4})/(?P<year2>\d{4})D(?P<doy>\d{3}).csv')),
        # '/mnt/data/labserver_files/METFiDAS/data/processed/measured/2005/2005M220.csv'
        ('ls2', re.compile('/mnt/data/labserver_files/METFiDAS/data/processed/measured/(?P<year>\d{4})/(?P<year2>\d{4})M(?P<doy>\d{3}).csv')),
        # '/mnt/data/labserver_files/METFiDAS-3/Level1/2014/2014-AVG5-237.csv'
        ('ls3', re.compile('/mnt/data/labserver_files/METFiDAS-3/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-AVG5-(?P<doy>\d{3}).csv')),
        # '/mnt/data/labserver_files/METFiDAS-3/Level1/2014/2014-MMX5-237.csv'
        ('ls4', re.compile('/mnt/data/labserver_files/METFiDAS-3/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-MMX5-(?P<doy>\d{3}).csv')),
        # '/mnt/data/labserver_files/METFiDAS-3/Level1/2014/2014-SMP1-237.csv'
        ('ls5', re.compile('/mnt/data/labserver_files/METFiDAS-3/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-SMP1-(?P<doy>\d{3}).csv')),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/2014/20140831_1hour.csv',
        ('ls6', re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour.csv')),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/2014/20140831_1hour_maxmin.csv',
        ('ls7', re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/1hour/(?P<year>\d{4})/(?P<date>\d{8})_1hour_maxmin.csv')),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/5min/2014/20140831_5min.csv',
        ('ls8', re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min.csv')),
        # '/mnt/data/labserver_files/METFiDAS-3/Level2/5min/2014/20140831_5min_maxmin.csv',
        ('ls9', re.compile('/mnt/data/labserver_files/METFiDAS-3/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min_maxmin.csv')),
    ],
    'SonicLicor-Incoming': [
        # '/mnt/data/SonicLicor-Incoming/Level1/2015/2015-SMP-223.csv'
        ('sli1', re.compile('/mnt/data/SonicLicor-Incoming/Level1/(?P<year>\d{4})/(?P<year2>\d{4})-SMP-(?P<doy>\d{3}).csv')),
    ],
    'Ceilometer-Incoming': [
        # '/mnt/data/Ceilometer-Incoming/Level2/1min/2016/20160604_1min.csv'
        ('ci1', re.compile('/mnt/data/Ceilometer-Incoming/Level2/1min/(?P<year>\d{4})/(?P<date>\d{8})_1min.csv')),
        # '/mnt/data/Ceilometer-Incoming/Level2/5min/2014/20140501_5min.csv'
        ('ci2', re.compile('/mnt/data/Ceilometer-Incoming/Level2/5min/(?P<year>\d{4})/(?P<date>\d{8})_5min.csv')),
    ],
    'LUMA': [
        # '/mnt/data/LUMA/RUAO/ReadingFlux_2015259.csv'
        ('luma1', re.compile('/mnt/data/LUMA/RUAO/ReadingFlux_(?P<date_doy>\d{7}).csv')),
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
    for name, pattern in instrument_patterns:
        match = re.match(pattern, path)
        if match:
            return name, pattern, match
    return name, None, None


def check_path_format(instrument_paths):
    pattern_matches = defaultdict(list)
    unmatched = defaultdict(list)
    for instrument, paths in instrument_paths.items():
        print(instrument)
        instrument_patterns = PATTERNS.get(instrument)
        if not instrument_patterns:
            print('  Pattern missing for {}'.format(instrument))
            continue

        for path in paths:
            name, pattern, match = check_path(instrument_patterns, path)
            if not match:
                # print('  Unmatched: {}'.format(path))
                unmatched[instrument].append(path)
            pattern_matches['{}:{}'.format(instrument, name)].append(match)
        print('  Unmatched count: {}'.format(len(unmatched[instrument])))
    return pattern_matches, unmatched


def check_date_parse(pattern_matches):
    for name, matches in pattern_matches.items():
        print(name)
