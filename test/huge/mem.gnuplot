set xlabel 'Pamiec[kB]'
set ylabel 'Ilosc obiektow'
set terminal pdf
set output 'mem.pdf'
plot "mem.out"
