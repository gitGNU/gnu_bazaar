#!/bin/sh

if [ $# != 2 ]; then
    echo usage: $0 "<repeat>" "<amount>"
    exit 1
fi

REPEAT=$1
AMOUNT=$2

for script in std bzr; do
    for i in $(seq $REPEAT); do
        python -O $script.py psycopg "dbname = ord port = 5433" -a $AMOUNT
    done | tee $script.out.01
done
