'Script that loads MODE3.py and exports useful info about e.g. datasets in declarative way.'
import os
import sys
import simplejson
from cStringIO import StringIO
import datetime as dt

import MODE3 as m3

IMPORT_DIR = '../Extractor/import_data'


def export(filename, data):
    if not os.path.exists(IMPORT_DIR):
        os.makedirs(IMPORT_DIR)

    full_path = os.path.join(IMPORT_DIR, filename + '.json')
    with open(full_path, 'w') as f:
        simplejson.dump(data, f, indent=2)


def get_datatype_vars():
    datasets = []
    for dt in m3.DATATYPES:
        var, varlong, vartype = m3.define_vars(dt, False)
        datasets.append({'name': dt, 'variables': zip(var, varlong, vartype)})
    return datasets


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

def gen_dir_file(data_type, dtuple, ymd_file):
    # Copied from MODE3.py.
    # Changed indentation.
    #dtuple=d.timetuple()
    #ymd_file=int(dtuple[0])*10000+int(dtuple[1])*100+int(dtuple[2])
    datadir, datafile = '', ''

    if data_type=="eddy_cov" and ymd_file >= 20150923:
        datadir='/home/webbie/micromet/LUMA/RUAO'
        datafile='ReadingFlux_'+str(dtuple[0]).zfill(3)+str(dtuple[7]).zfill(3)+'.csv'
    elif data_type=="cloudbase_5min" and ymd_file >= 20150319:
        datadir='/export/its/labs/Ceilometer-Incoming/Level2/5min/'+str(dtuple[0])
        datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min.csv'
    elif data_type=="cloudbase_1min":
        datadir='/export/its/labs/Ceilometer-Incoming/Level2/1min/'+str(dtuple[0])
        datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1min.csv'
    elif data_type=="climat0900":
        if ymd_file >= 20150416:
            # datadir='/export/labserver/data/METFiDAS-3/Level2/climat'
            datadir='/export/its/labs/METFiDAS-Incoming/Level2/climat'
            datafile=str(dtuple[0])+'climat.csv'
        elif ymd_file >= 20140901:
            datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/climat'
            datafile=str(dtuple[0])+'climat.csv'
    elif data_type=="Vertical_profiles":
        if ymd_file >= 20150819:
            # datadir='/export/labserver/data/METFiDAS-3/Level2/climat'
            datadir='/export/its/labs/METFiDAS-Incoming/Level2/profile/'+str(dtuple[0])
            datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_UTprofile.csv'
    else:
        if ymd_file >= 20150429:
            if data_type=="1sec_Level1":
                # datadir='/export/labserver/data/METFiDAS-3/Level1/'+str(dtuple[0])
                datadir='/export/its/labs/METFiDAS-Incoming/Level1/'+str(dtuple[0])
                datafile=str(dtuple[0]).zfill(3)+'-SMP1-'+str(dtuple[7]).zfill(3)+'.csv'
            elif data_type=="5min_Level1":
                # datadir='/export/labserver/data/METFiDAS-3/Level1/'+str(dtuple[0])
                datadir='/export/its/labs/METFiDAS-Incoming/Level1/'+str(dtuple[0])
                datafile=str(dtuple[0]).zfill(3)+'-AVG5-'+str(dtuple[7]).zfill(3)+'.csv'
            elif data_type=="5min_Level1_maxmin":
                # datadir='/export/labserver/data/METFiDAS-3/Level1/'+str(dtuple[0])
                datadir='/export/its/labs/METFiDAS-Incoming/Level1/'+str(dtuple[0])
                datafile=str(dtuple[0]).zfill(3)+'-MMX5-'+str(dtuple[7]).zfill(3)+'.csv'
            elif data_type=="5min_Level2":
                # datadir='/export/labserver/data/METFiDAS-3/Level2/5min/'+str(dtuple[0])
                datadir='/export/its/labs/METFiDAS-Incoming/Level2/5min/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min.csv'
            elif data_type=="5min_Level2_maxmin":
                # datadir='/export/labserver/data/METFiDAS-3/Level2/5min/'+str(dtuple[0])
                datadir='/export/its/labs/METFiDAS-Incoming/Level2/5min/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min_maxmin.csv'
            elif data_type=="1hour_Level2":
                # datadir='/export/labserver/data/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
                datadir='/export/its/labs/METFiDAS-Incoming/Level2/1hour/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour.csv'
            elif data_type=="1hour_Level2_maxmin":
                # datadir='/export/labserver/data/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
                datadir='/export/its/labs/METFiDAS-Incoming/Level2/1hour/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour_maxmin.csv'
            elif data_type=="soniclicor_Level1":
                datadir='/export/its/labs/SonicLicor-Incoming/Level1/'+str(dtuple[0])
                datafile=str(dtuple[0]).zfill(3)+'-SMP-'+str(dtuple[7]).zfill(3)+'.csv'
        elif ymd_file >= 20140901:
            if data_type=="1sec_Level1":
                datadir='/export/its/labs/labserver_files/METFiDAS-3/Level1/'+str(dtuple[0])
                datafile=str(dtuple[0]).zfill(3)+'-SMP1-'+str(dtuple[7]).zfill(3)+'.csv'
            elif data_type=="5min_Level1":
                datadir='/export/its/labs/labserver_files/METFiDAS-3/Level1/'+str(dtuple[0])
                datafile=str(dtuple[0]).zfill(3)+'-AVG5-'+str(dtuple[7]).zfill(3)+'.csv'
            elif data_type=="5min_Level1_maxmin":
                datadir='/export/its/labs/labserver_files/METFiDAS-3/Level1/'+str(dtuple[0])
                datafile=str(dtuple[0]).zfill(3)+'-MMX5-'+str(dtuple[7]).zfill(3)+'.csv'
            elif data_type=="5min_Level2":
                datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/5min/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min.csv'
            elif data_type=="5min_Level2_maxmin":
                datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/5min/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min_maxmin.csv'
            elif data_type=="1hour_Level2":
                datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour.csv'
            elif data_type=="1hour_Level2_maxmin":
                datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
                datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour_maxmin.csv'
    return datadir, datafile


if __name__ == '__main__':
    datasets = get_datatype_vars()

    longnames = get_datatype_longnames()

    for ds in datasets:
        ds['longname'] = longnames[ds['name']]
    dtuple = ('{year}', '{month}', '{day}', '{hour}', '{minute}', '{second}', '{wday}', '{yday}')
    ymd_breaks = [
        20150923,
        20150319,
        20150416,
        20140901,
        20150819,
        20150429,
        20140901]

    for ds in datasets:
        print(ds['name'])
        datadirs = []
        datafiles = []

        datadir_ymds = []
        datafile_ymds = []


        for ymd_break in sorted(ymd_breaks):
            for ymd in [ymd_break - 1, ymd_break]:
                datadir, datafile = gen_dir_file(ds['name'], dtuple, ymd)
                if datadir and datadir not in datadirs:
                    datadirs.append(datadir)
                    datadir_ymds.append(ymd)
                if datafile and datafile not in datafiles:
                    datafiles.append(datafile)
                    datafile_ymds.append(ymd)

        print(datadirs)
        print(datadir_ymds)
        print(datafiles)
        print(datafile_ymds)
        ds['datadirs'] = datadirs
        ds['datadir_ymds'] = datadir_ymds
        if len(datafiles) != 1:
            raise Exception('unexpected datafile length')
        ds['datafile'] = datafiles[0]

    export('datasets', datasets)


