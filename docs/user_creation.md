User Creation
=============

There is no web-based interface for creating users, instead they should be created from the command
line. 

    cd Extractor
    source setup_flask.sh
    flask shell

```python
# Creates new user "Steve" in database
from Extractor.models import User
from Extractor.database import db_session
steve = User('Steve', 'steve@rdg.ac.uk', 'secure_p4ssw0rd')
db_session.add(steve)
db_session.commit()
```

If you navigate to the users page, this user will appear (must be logged in to do this).
