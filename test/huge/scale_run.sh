#!/bin/sh

if [ $# != 1 ]; then
    echo usage: $0 "<max>"
    exit 1
fi

MAX=$1

for i in $(seq 1000 1000 $MAX); do
    ./scale.py psycopg 'dbname = ord port = 5433' $i
done | tee scale.out

gnuplot <<END
set xlabel 'Ilosc obiektow'
set ylabel 'Czas[s]'
set terminal pdf
set output 'scale.pdf'
plot "scale.out" with points pointtype 3, 0.005*x+8
END
