#!/bin/bash

# populate database
STATS_DB0='stats0.db'
STATS_DB1='stats1.db'
STATS_DB2='stats2.db'


    mkdir -p var/log
    sqlite3 ./var/$STATS_DB0 < ./share/stats.sql 
    sqlite3 ./var/$STATS_DB1 < ./share/stats.sql  && \
    sqlite3 ./var/$STATS_DB2 < ./share/stats.sql  && \
    python3 ./bin/stats_populate.py

