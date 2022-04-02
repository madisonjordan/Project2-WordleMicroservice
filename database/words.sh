#!/bin/bash
cat /usr/share/dict/words | grep -x '[a-z]\{5\}' > words.json