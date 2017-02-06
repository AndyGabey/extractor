Development Installation
========================

    git clone https://github.com/AndyGabey/extractor
    cd extractor

    # Unzip test data.
    mkdir -p demo_data/metfidas
    cd demo_data/metfidas
    tar xvf ../../test_data/2015-SMP1-086.csv.tgz
    cd ../../

    # Setup/activate venv.
    virtualenv venv
    source venv/bin/activate
    # sudo aptitude install python-dev
    pip install -r requirements.txt
    pip install -e .

    # Setup dev env.
    cd extractor
    cp host_config.txt.tpl host_config.txt
    export FLASK_APP=extractor
    export FLASK_DEBUG=true
    flask shell # Opens ipython shell:

```python
# Creates db and populates it with some mock data.
from extractor.database import init_db
init_db(True)
```

Running
-------

    cd extractor
    source venv/bin/activate
    export FLASK_APP=extractor
    export FLASK_DEBUG=true
    flask run


Then go to: http://127.0.0.1:5000/

Try also:

http://127.0.0.1:5000/dataset/AWS/get_data?start_date=2015-03-27-00:00:11&end_date=2015-03-27-00:00:21&field=P&field=RH&data_format=html
