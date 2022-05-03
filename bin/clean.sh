#!/bin/bash
rm -r \
    build \
    dist \
    var \
    bin/__pycache__ \
    dump.rdb \
    *.spec \
    traefik \
    2> /dev/null 
#remove crontab
crontab -r