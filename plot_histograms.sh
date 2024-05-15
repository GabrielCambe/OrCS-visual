#!/bin/bash
for folder in add_imediate*
do
    for filename in $(ls $folder/*.txt)
        do
            base=${filename%.*}
            name=${base#*/}
            echo python plot_histogram.py -i "./$filename" -o ./$folder/$name -p $1 $2
            python plot_histogram.py -i "./$filename" -o ./$folder/$name -p $1 $2
        done
done
