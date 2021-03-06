mapping =  { 
        '1sec_Level1': {
            'datafile': '{year}-SMP1-{yday}.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level1/{year}',
            'longname': '1-sec \"instantaneous\" logger output',
            'datetime_fmt': '%d/%m/%Y %H:%M:%S',
            'date_col_name': 'TimeStamp',
            },
        '5min_Level1': {
            'datafile': '{year}-AVG5-{yday}.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level1/{year}',
            'longname': '5-min averaged logger output',
            'datetime_fmt': '%d/%m/%Y %H:%M:%S',
            'date_col_name': 'TimeStamp',
            },
        '5min_Level1_maxmin': {
            'datafile': '{year}-MMX5-{yday}.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level1/{year}',
            'longname': '5-min max/min logger output',
            'datetime_fmt': '%d/%m/%Y %H:%M:%S',
            'date_col_name': 'TimeStamp',
            },
        '5min_Level2': {
            'datafile': '{year}{month}{day}_5min.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level2/5min/{year}',
            'longname': '5-min WMO-standard processed output',
            'date_col_name': 'TimeStamp',
            'time_col_name': 'Time',
            },
        '5min_Level2_maxmin': {
            'datafile': '{year}{month}{day}_5min_maxmin.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level2/5min/{year}',
            'longname': '5-min max/min processed output',
            'date_col_name': 'TimeStamp',
            'time_col_name': 'Time',
            },
        '1hour_Level2': {
            'datafile': '{year}{month}{day}_1hour.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level2/1hour/{year}',
            'longname': '1-hour WMO-standard processed output',
            'date_col_name': 'TimeStamp',
            'time_col_name': 'Time',
            },
        '1hour_Level2_maxmin': {
            'datafile': '{year}{month}{day}_1hour_maxmin.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level2/1hour/{year}',
            'longname': '1-hour max/min processed output',
            'date_col_name': 'TimeStamp',
            'time_col_name': 'Time',
            },
        'climat0900': {
            'datafile': '{year}climat.csv',
            'datadir': 'labserver_files/METFiDAS-3/Level2/climat',
            'longname': '0900 UTC climat observation - no data thrown back',
            'date_col_name': 'TimeStamp',
            'time_col_name': 'hhmm',
            },
        'soniclicor_Level1': {
            'datafile': '{year}-SMP-{yday}.csv',
            'datadir': 'SonicLicor-Incoming/Level1/{year}',
            'longname': '0.1-sec sonic licor output',
            'datetime_fmt': '%d/%m/%Y %H:%M:%S.%f',
            'date_col_name': 'TimeStamp',
            },
        'Vertical_profiles': {
            'datafile': '{year}{month}{day}_UTprofile.csv',
            'datadir': 'metfidas/Level2/profile/{year}',
            'longname': 'Vertical profiles of wind and temperature',
            'date_col_name': 'TimeStamp',
            'time_col_name': 'Time',
            },
        'eddy_cov': {
            'datafile': 'ReadingFlux_{year}{yday}.csv',
            'datadir': 'LUMA/RUAO',
            'longname': 'Eddy covariances - 30-min averages',
            'datetime_fmt': '%Y-%m-%d %H:%M:%S',
            'date_col_name': 'TIME',
            },
        'cloudbase_5min': {
            'datafile': '{year}{month}{day}_5min.csv',
            'datadir': 'Ceilometer-Incoming/Level2/5min/{year}',
            'longname': 'Cloud base averages at 5 minute intervals',
            'date_col_name': 'Date',
            'time_col_name': 'Time',
            },
        'cloudbase_1min': {
            'datafile': '{year}{month}{day}_1min.csv',
            'datadir': 'Ceilometer-Incoming/Level2/1min/{year}',
            'longname': 'Cloud base averages at 1 minute intervals',
            'date_col_name': 'Date',
            'time_col_name': 'Time',
            }
        }
