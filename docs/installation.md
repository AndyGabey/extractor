Development Installation
========================

    # Install dependencies  (Ubuntu assumed)
    apt-get update
    apt-get install python-pip
    apt-get install python-virtualenv
    
    # The following commands may need to be executed as sudo
    git clone https://github.com/AndyGabey/extractor Extractor
    cd Extractor

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
    cd Extractor
    
    # Set for production config mode (sets logging level)
    echo "Extractor.config.ProductionConfig" > host_config.txt
    # Or: set for development config:
    # cp host_config.txt.tpl host_config.txt
    ```python
# Creates db and populates it with some mock data.
from Extractor.database import init_db
init_db()
```
    # Make sure db folder writable
    chmod 777 db
    cd db
    chmod 777 extractor.db
    
    
Setting up for actual running
------------------
    cd ../docs
    cp Extractor.conf /etc/apache2/sites-available
    cd /etc/apache2/sites-enabled
    ln ../sites-available/Extractor.conf Extractor.conf
    systemctl restart apache2
    
Setting up dev version
--------------
    export FLASK_APP=Extractor
    export FLASK_DEBUG=true
    cd ..
    flask shell # Opens ipython shell:



Running Local Copy
------------------

    cd Extractor
    source setup_flask.sh
    flask run


Running Command Line Interface
------------------------------

    cd Extractor
    source setup_flask.sh
    flask shell


Then go to: http://127.0.0.1:5000/
