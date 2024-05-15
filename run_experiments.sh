#!/bin/bash
for folder in $(ls -d ./histograms/*) 
do
    for filename in $(ls "$folder")
    do
        base=${filename%.*}
        echo python tool.py -t $folder/$filename -o $folder/${base%.*} -p -x
        echo ""
        # xvfb-run python tool.py -t $folder/$filename -o $folder/${base%.*} -p -x > $folder/${base%.*}-log.out
        # python tool.py -t $folder/$filename -o $folder/${base%.*} -p -x > $folder/${base%.*}-log.out
    done
done