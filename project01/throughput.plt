clear
reset
unset key
set title "Throughput"
set key inside top right
set style data histogram
set style histogram cluster gap 1
set yrange[0:10600]
set style fill solid border
set boxwidth 0.9
set xlabel "Type"
set ylabel "Bytes per Second"
unset x2tics
plot 'throughput.dat' u 2:xticlabels(1) title "Non-Forking", '' u 3:xticlabels(1) title "Forking Enabled"
set term png
set output "throughput.png"
replot 
set term x11
