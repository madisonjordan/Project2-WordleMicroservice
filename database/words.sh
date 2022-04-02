#!/bin/bash

# Populate word database with five-letter words (without caps, punc, or non-ASCII)
grep -x '[a-z]\{5\}' /usr/share/dict/words \
| sqlite-utils insert words.db words - \
    --text --convert '({"word": w} for w in text.split())'


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