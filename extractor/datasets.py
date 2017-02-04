from collections import OrderedDict as od

DATASETS = od([
    ('AWS logger output', od([
        ('1sec_Level1', '1-sec "instantaneous" logger output'),
        ('5min_Level1', '5-min averaged logger output'),
        ('5min_Level1_maxmin', '5-min max/min logger output'),
    ])),
    ('AWS processed output', od([
        ('5min_Level2 checked', '5-min WMO-standard processed output'),
        ('5min_Level2_maxmin', '5-min max/min processed output'),
        ('1hour_Level2', '1-hour WMO-standard processed output'),
        ('1hour_Level2_maxmin', '1-hour max/min processed output'),
    ])),
    ('Climate observations', od([
        ('climat0900', '0900 UTC METFiDAS climate observation - no data thrown back'),
    ])),
    ('Sonic licor', od([
        ('soniclicor_Level1', '0.1-sec sonic licor output'),
    ])),
    ('Vertical profiles', od([
        ('Vertical_profiles', 'Vertical profiles of wind and temperature'),
    ])),
    ('Eddy covariances', od([
        ('eddy_cov', 'Eddy covariances - 30-min averages'),
    ])),
    ('Cloud base average', od([
        ('cloudbase_5min', 'Cloud base averages at 5-minute intervals'),
        ('cloudbase_1min', 'Cloud base averages at 1-minute intervals'),
    ]))
])
