#!/bin/bash

# Directory containing the .events.paje files
dir="."

# Iterate over all .events.paje files in the directory
for file in "$dir"/*/*.events.paje
do
    # Run count_number_of_events.sh on the file
    echo "$file"
    ./count_number_of_events.sh "$file"
done