import os
import sys
from timeit import default_timer as timer

import psutil

DATAFILE = '../demo_data/metfidas/2015-SMP1-086.csv'

expts = ['pandas', 'csv', 'manual']

# Thanks: 
# http://fa.bianp.net/blog/2013/different-ways-to-get-memory-consumption-or-lessons-learned-from-memory_profiler/
def memory_usage_psutil():
    # return the memory usage in MB
    process = psutil.Process(os.getpid())
    mem = process.memory_full_info().uss / float(2 ** 20)
    return mem


def print_mem(msg):
    print('{0}: {1:.1f} MB'.format(msg, memory_usage_psutil()))


def main(expt):
    print('Expt: ' + expt)
    print_mem('Base usage')
    start = timer()
    cols = ['RH', 'P']
    if expt not in expts:
        raise Exception('Unknown expt')

    if expt == 'pandas':
        res = test_pandas(cols)
    elif expt == 'csv':
        res = test_csv(cols)
    elif expt == 'manual':
        res = test_manual(cols)
    print_mem('CSV parsed')
    outfile = 'parse_csv_{}.json'.format(expt)
    with open(outfile, 'w') as f:
        f.write(res)
    end = timer()
    print('Ran in {0:.3f} s'.format(end - start))


def test_pandas(cols):
    import pandas as pd
    print_mem('Libs loaded')
    df = pd.read_csv(DATAFILE)
    return df[cols].to_json()


def test_csv(cols):
    import csv
    print_mem('Libs loaded')
    rows = []
    with open(DATAFILE, 'r') as f:
        reader = csv.reader(f)
        header = reader.next()
        col_indices = []
        for i, col in enumerate(header):
            if col in cols:
                col_indices.append(i)
        reader.next()

        for row in reader:
            for i in col_indices:
                rows.append(row[i])
    return ','.join(rows)


def test_manual(cols):
    print_mem('Libs loaded')
    rows = []
    with open(DATAFILE, 'r') as f:
        for line in f.readlines():
            rows.append(line.split(','))

if __name__ == '__main__':
    main(sys.argv[1])