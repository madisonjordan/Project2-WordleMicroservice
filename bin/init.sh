#!/bin/bash

echo "export PROJ_PATH=$(pwd)" > ~/wordle.env && . ~/wordle.env

# start redis-server in background
redis-server --daemonize yes

#############
#  traefik  #
#############

# install traefik depdendency
mkdir temp
curl --silent -L -o traefik.tar.gz https://github.com/traefik/traefik/releases/download/v2.6.3/traefik_v2.6.3_linux_amd64.tar.gz
tar -xf traefik.tar.gz -C temp 2>&1 1>/dev/null
mv ./temp/traefik . 
rm -rf temp
rm traefik.tar.gz

####################
# leaderboard app  #
####################


# build standalone app
pyinstaller --onefile ./bin/python/getTop10.py

# load crontab
crontab ./bin/cron.leaderboard.txt && mkdir -p ./var/log
