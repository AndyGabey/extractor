Observatory data extractor website
==================================

* Based on a flask webapp, served by apache, using WSGI as the interface.
* Uses SQLAlchemy/sqlite3 for the metadata.
* Uses jinja2 for the templating.
* Frontend uses jquery.
* Data is stored in CSV files, read on demand and the required fields taken from them.
