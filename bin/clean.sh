#!/bin/bash
rm -r \
    build \
    dist \
    var \
    ./**/__pycache__ \
    dump.rdb \
    *.spec \
    traefik \
    ~/wordle.env \
    2> /dev/null 
#remove crontab
crontab -r