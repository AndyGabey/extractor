'Script that loads MODE3.py and exports useful info about e.g. datasets in declarative way.'
import os
import sys
import simplejson
from cStringIO import StringIO

import MODE3 as m3

IMPORT_DIR = '../extractor/import_data'


def export(filename, data):
    if not os.path.exists(IMPORT_DIR):
        os.makedirs(IMPORT_DIR)

    full_path = os.path.join(IMPORT_DIR, filename + '.json')
    with open(full_path, 'w') as f:
        simplejson.dump(data, f, indent=2)


def get_datatype_vars():
    datatype_vars = []
    for dt in m3.DATATYPES:
        var, varlong, vartype = m3.define_vars(dt, False)
        datatype_vars.append({'name': dt, 'variables': zip(var, varlong, vartype)})
    return datatype_vars


def get_datatype_longnames():
    stdout = sys.stdout
    sys.stdout = StringIO()
    m3.set_data_type()
    out = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = stdout

    lines = out.split('\n')
    longnames = {}
    for line in lines:
        if line.find('value=') == -1:
            continue
        input_end = line.rfind('>')
        value_end = line.rfind('value=') + 7
        longnames[line[value_end:line.find('"', value_end + 2)]] = line[input_end + 1:]
    return longnames


if __name__ == '__main__':
    datatype_vars = get_datatype_vars()

    longnames = get_datatype_longnames()

    for dt in datatype_vars:
        dt['longname'] = longnames[dt['name']]
    export('datasets', datatype_vars)
