#!/bin/bash
el=$(head -n2 RDFDAT | tail -n 1 | awk '{print $2+1}')
tail -n $(wc -l RDFDAT | awk '{print ($1-2)}') RDFDAT | split --lines=$el
paste x*| head -n1|awk '{printf "#           # ";for (i=1;i<=NF;i+=2) printf "%2s %2s        # ", $i,$(i+1);printf "\n"}' > rdfhead
paste x*| awk  '{printf "%s  ", $1 ;for (i=2;i<=NF;i+=2) printf "%s  ", $i; printf "\n" }' > rdf_temp.dat
cat rdfhead rdf_temp.dat > rdf_alla.dat 
sed "2d" rdf_alla.dat > rdf_all.dat
rm rdfhead rdf_temp.dat rdf_alla.dat
python3 ~/bin/grtotmaker/make_SFQiG.py
