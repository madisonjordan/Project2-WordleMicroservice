#!/bin/bash

# populate database
DB='stats.db'


if [ ! -f "./var/$DB" ]
then
    mkdir -p var/log
    sqlite3 ./var/$DB < ./share/stats.sql && \
    python3 ./bin/stats_users_populate.py
else
    echo "$DB already exists"
fi
