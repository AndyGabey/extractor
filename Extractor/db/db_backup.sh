#!/usr/bin/env bash
mkdir -p backup
NOW=`date +'%Y%m%d_%H'`
sqlite3 extractor.db ".backup backup/extractor.db.$NOW.bak"
