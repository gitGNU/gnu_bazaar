#!/bin/sh

if [ $# = 1 ]; then
    REPEAT=$1
else
    REPEAT=1
fi

AMOUNT=100000

while [ $REPEAT -gt 0 ]; do
    python -O add.py psycopg 'dbname = ord port = 5433' -a $AMOUNT -n
    python -O add.py psycopg 'dbname = ord port = 5433' -a $AMOUNT
    REPEAT=$(($REPEAT-1))
done | tee "add: $(date +'%Y-%m-%d.%H:%M:%S').log"
