#!/usr/bin/env bash
sqlite3 extractor.db ".backup extractor.db.bak"
cp $1 extractor.db
chmod 777 extractor.db
