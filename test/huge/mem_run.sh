#!/bin/sh

if [ $# != 1 ]; then
    echo usage: $0 "<max>"
    exit 1
fi

MAX=$1

for i in $(seq 1000 1000 $MAX); do
    python -O ./mem.py psycopg 'dbname = ord port = 5433' $i
done | tee mem.out

gnuplot <<END
set xlabel 'Ilosc obiektow'
set ylabel 'Pamiêæ[kB]'
set terminal pdf
set output 'mem.pdf'
plot "mem.out" with points pointtype 3, 0.3*x+8752
END
