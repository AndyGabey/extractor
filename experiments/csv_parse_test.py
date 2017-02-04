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
    if expt not in expts:
        raise Exception('Unknown expt')
    if expt == 'pandas':
        test_pandas()
    elif expt == 'csv':
        test_csv()
    elif expt == 'manual':
        test_manual()
    end = timer()
    print('Ran in {0:.3f} s'.format(end - start))


def test_pandas():
    import pandas as pd
    print_mem('Libs loaded')
    df = pd.read_csv(DATAFILE)
    print_mem('CSV parsed')


def test_csv():
    import csv
    print_mem('Libs loaded')
    rows = []
    with open(DATAFILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    print_mem('CSV parsed')


def test_manual():
    print_mem('Libs loaded')
    rows = []
    with open(DATAFILE, 'r') as f:
        for line in f.readlines():
            rows.append(line.split(','))
    print_mem('CSV parsed')

if __name__ == '__main__':
    main(sys.argv[1])
