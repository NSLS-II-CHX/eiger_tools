#!/bin/bash

location="http://192.168.20.68/data/"
datadir="./data/"

download=$(wget -nd -d -p -r -np -N --spider $location  2>&1 | grep " -> " | grep -Ev "\/\?C=" | sed "s/.* -> //" |grep -e "/data/"|grep  -v "/\.")
for i in $download; do
   echo -n "Move" ${i##$location} "..."
   curl --create-dirs -s -X GET -o $datadir${i##$location} $i && curl -s -X DELETE $i
   echo "done."
done




