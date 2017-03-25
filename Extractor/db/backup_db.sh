#!/usr/bin/env bash
NOW=`date +'%Y%m%d_%H'`
sqlite3 extractor.db ".backup extractor.db.$NOW.bak"
