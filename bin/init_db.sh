#!/bin/bash

#################
#   words.db    #
#################

# Populate word database with five-letter words (without caps, punc, or non-ASCII)
DB='words.db'

if [ ! -f "./var/$DB" ]
then
    mkdir -p var/log
    grep -x '[a-z]\{5\}' /usr/share/dict/words \
    | sqlite-utils insert "./var/$DB" words - \
        --text --convert '({"word": w} for w in text.split())' --pk=word && \
    echo "Created '$DB'"
else
    echo "'$DB' already exists"
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
if [ ! -f "./var/$DB" ]
then
    mkdir -p var/log
    echo -e $parseanswer | sqlite-utils insert ./var/$DB answers - \
    --text --convert '({"word": w} for w in text.split())' \
    && cat ./bin/python/date_gen.py | sqlite-utils convert ./var/$DB answers rowid - --output day \
    && sqlite-utils transform ./var/$DB answers --pk day --column-order day --column-order word && \
    echo "Created '$DB'"
else
    echo "'$DB' already exists"
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

#download population script
if [ ! -f "./share/sqlite3-populated.sql" ]
then
    mkdir -p ./share && \
    curl --silent -L -o sqlite3-populated.sql https://raw.githubusercontent.com/ProfAvery/cpsc449/master/stats/share/sqlite3-populated.sql && \
    mv ./sqlite3-populated.sql ./share && \
    echo "Downloaded 'sqlite3-populated.sql'"
else
    echo "'sqlite3-populated.sql' already exists"
fi


# build full statistics.db if it doesn't exist
if [ ! -f "./var/stats_full.db" ]
then
    sqlite3 ./var/stats_full.db < ./share/sqlite3-populated.sql && \
    echo "Populated 'stats_full.db'"
else
    echo "'stats_full.db' already exists"
fi


# create stats shards
STATS_DB0='stats0.db'
STATS_DB1='stats1.db'
STATS_DB2='stats2.db'


mkdir -p var/log
sqlite3 ./var/$STATS_DB0 < ./share/stats.sql  && \
sqlite3 ./var/$STATS_DB1 < ./share/stats.sql  && \
sqlite3 ./var/$STATS_DB2 < ./share/stats.sql  

# shard database
python3 ./bin/python/stats_shard.py

# remove full stats.db
rm ./var/stats_full.db && \
echo "Removed 'stats_full.db'"
