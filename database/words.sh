#!/bin/bash
grep -x '[a-z]\{5\}' /usr/share/dict/words \
|sqlite-utils insert words.db words - \
    --text --convert '({"word": w} for w in text.split())'
    