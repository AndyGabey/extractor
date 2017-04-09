import datetime as dt
from collections import Counter

from Extractor.data_extractor import DataExtractor
from Extractor.models import Dataset

DATES = {
    'soniclicor_Level1': (dt.datetime(2016, 1, 1, 23), dt.datetime(2016, 1, 2, 1)),
    'Vertical_profiles': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5)),
    'eddy_cov': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5)),
    'cloudbase_5min': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5)),
    'cloudbase_1min': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5))
}

exts = [DataExtractor(ds.name, None) for ds in Dataset.query.all()]
not_floats = Counter()
num_vals = 0
for ext in exts:
    try:
        print(ext.dataset_name)
        ext.load()
        if ext.dataset_name in DATES:
            dates = DATES[ext.dataset_name]
        else:
            dates = (dt.datetime(2015, 1, 1), dt.datetime(2015, 1, 3))

        ext._set(dates[0], dates[1], [v.var for v in ext.dataset.variables], None, 'json')
        ext.generate_filelist()
        ext.extract_data()
        print('  Extracted data')
        # print('  cols: {}'.format(ext.cols))
        print('  # rows: {}'.format(len(ext.rows)))

        for row in ext.rows:
            if len(row) != len(ext.cols):
                print('    Row wrong length: row: {}, cols: {}'.format(len(row), len(ext.cols)))
            for cell in row[1:]:
                try:
                    val = float(cell)
                    num_vals += 1
                except:
                    not_floats[cell] += 1

        if False:
            for row in ext.rows[:5]:
                print('    {}'.format(row))
            for row in ext.rows[-5:]:
                print('    {}'.format(row))
    except Exception as e:
        print('  PROBLEM EXTRACTING DATA')
        print('    {}'.format(e))

print('################')
print('Num values: {}'.format(num_vals))
print('Unparsable as floats:')
for cell, count in not_floats.most_common():
    print('{}: {}'.format(cell, count))
