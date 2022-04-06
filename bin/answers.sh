#!/bin/bash

# load json file using python
PARSE=`python - <<'EOF'
import json;
file = open('./share/answers.json');
answers = json.load(file);
file.close();
for i in answers:
    print(i);
EOF`

# populate database
DB='answers.db'

if [ ! -f "./var/$DB" ]
then
    mkdir -p var/log
    echo ${PARSE} | sqlite-utils insert ./var/$DB answers - \
    --text --convert '({"word": w} for w in text.split())' --pk=word 
else
    echo "$DB already exists"
fi
