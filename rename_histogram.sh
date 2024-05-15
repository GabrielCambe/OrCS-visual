#!/bin/bash
for folder in add_imediate*
do
    for filename in ./$folder/*.pdf
        do
            mod=${filename//[\"]/}
            mv $filename $mod 
        done
done

