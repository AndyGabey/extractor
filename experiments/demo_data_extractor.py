import os
from collections import Counter
import csv
import hashlib

DATAROOT = '../demo_data/Extractor'

def main():
    if not os.path.exists(DATAROOT):
        raise Exception('Unzip ExtractorTestData.zip to the ../demo_data dir')

    counter = Counter()
    for root, dirs, files in os.walk(DATAROOT):
        #print((root, dirs, files))
        for filename in files:
            if os.path.splitext(filename)[-1].lower() == '.csv':
                header = process_csv(os.path.join(root, filename))
                counter[header] += 1
    return counter


def process_csv(filename):
    print(filename)
    with open(filename, 'r') as f:
        reader = csv.reader(f)

        header = reader.next()
        units = reader.next()
        #print(header)
        #print(units)
        rows = []
        for row in reader:
            rows.append(row)
        print(len(rows))
    return hashlib.sha1(''.join(header)).hexdigest()[:10]


if __name__ == '__main__':
    counter = main()
