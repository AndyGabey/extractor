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
    pip install -r requirements.txt

    # Setup dev env.
    cd extractor
    cp host_config.txt.tpl host_config.txt

Running
-------

    cd extractor
    source venv/bin/activate
    cd extractor
    python main.py

Then go to: http://127.0.0.1:5000/

Try also:

http://127.0.0.1:5000/get\_data?start\_date=2015-03-27-00:00:11&end\_date=2015-03-27-00:00:21&field=P&field=RH&data\_format=html
