set xlabel 'Ilosc obiektow'
set ylabel 'Pamiec[kB]'
set terminal pdf
set output 'mem.pdf'
plot "mem.out"
