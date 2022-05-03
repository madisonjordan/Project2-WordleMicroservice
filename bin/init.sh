#!/bin/bash

echo "export PROJ_PATH=$(pwd)" >> ~/.bash_profile

#################
#   words.db    #
#################

# Populate word database with five-letter words (without caps, punc, or non-ASCII)
DB='words.db'

if [ ! -f "$PROJ_PATH/var/$DB" ]
then
    mkdir -p var/log
    grep -x '[a-z]\{5\}' /usr/share/dict/words \
    | sqlite-utils insert "$PROJ_PATH/var/$DB" words - \
        --text --convert '({"word": w} for w in text.split())' --pk=word
else
    echo "$DB already exists"
fi

#####################################
# sqlite-utils schema words.db      #
#                                   #
#   CREATE TABLE [words] (          #
#       [word] TEXT                 #
#   );                              #
#                                   #
#####################################

#####################################################
# sqlite-utils analyze-tables words.db words       #
#                                                   #
# words.word: (1/1)                                 #
#                                                   #
#  Total rows: 4594                                 #
#  Null rows: 0                                     #
#  Blank rows: 0                                    #
#                                                   #
#  Distinct values: 4594                            #
#                                                   #
#####################################################




#################
#  answers.db   #
#################

# use `python3 -m pip install sqlite-utils` to load answers.db and run with ./bin/answers.sh
# load json file using python
parseanswer=$(
python3 - <<EOF
import json;
file = open('./share/answers.json');
answers = json.load(file);
file.close();
for word in answers:
    print(word); 
EOF
)

# populate database
DB='answers.db'

# create table from answers
# add column to answers.db for dates - starting at (start_day) + 1 day
# use "day" column as primary key
if [ ! -f "$PROJ_PATH/var/$DB" ]
then
    mkdir -p var/log
    echo -e $parseanswer | sqlite-utils insert $PROJ_PATH/var/$DB answers - \
    --text --convert '({"word": w} for w in text.split())' \
    && cat $PROJ_PATH/bin/python/date_gen.py | sqlite-utils convert $PROJ_PATH/var/$DB answers rowid - --output day \
    && sqlite-utils transform $PROJ_PATH/var/$DB answers --pk day --column-order day --column-order word
else
    echo "$DB already exists"
fi


#############################################
# CREATE TABLE "answers" (                  #
#   [day] TEXT PRIMARY KEY,                 #
#   [word] TEXT                             #
# );                                        #
#############################################


#################
#     stats     #
#################

# populate database
STATS_DB0='stats0.db'
STATS_DB1='stats1.db'
STATS_DB2='stats2.db'


mkdir -p var/log
sqlite3 $PROJ_PATH/var/$STATS_DB0 < $PROJ_PATH/share/stats.sql 
sqlite3 $PROJ_PATH/var/$STATS_DB1 < $PROJ_PATH/share/stats.sql  && \
sqlite3 $PROJ_PATH/var/$STATS_DB2 < $PROJ_PATH/share/stats.sql  && \
python3 $PROJ_PATH/bin/python/stats_populate.py


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
pyinstaller --onefile $PROJ_PATH/bin/python/getTop10.py

# start cronjob
crontab $PROJ_PATH/bin/cron.leaderboard.txt
