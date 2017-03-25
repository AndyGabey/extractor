import datetime as dt

from Extractor.models import Dataset, Variable
from Extractor.data_extractor import DataExtractor

DATES = {
        'soniclicor_Level1': (dt.datetime(2016, 1, 1, 23), dt.datetime(2016, 1, 2, 1)),
        'Vertical_profiles': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5)),
        'eddy_cov': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5)),
        'cloudbase_5min': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5)),
        'cloudbase_1min': (dt.datetime(2016, 1, 1), dt.datetime(2016, 1, 5))
        }

exts = [DataExtractor(ds.name, None) for ds in Dataset.query.all()]
for ext in exts:
    try:
        print(ext.dataset_name)
        ext.load()
        if ext.dataset_name in DATES:
            dates = DATES[ext.dataset_name]
        else:
            dates = (dt.datetime(2015, 1, 1), dt.datetime(2015, 1, 3))

        ext._set(dates[0], dates[1], ext.dataset.variables[1:3], None, 'json')
        ext.generate_filelist()
        ext.extract_data()
        print('  Extracted data')
    except Exception as e:
        print('  PROBELM EXTRACTING DATA')
        print('    {}'.format(e))
