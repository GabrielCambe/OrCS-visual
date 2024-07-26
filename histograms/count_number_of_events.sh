#!/bin/bash

# Check if a file name is provided
if [ -z "$1" ]
then
    echo "No file name provided. Usage: ./script.sh filename"
    exit 1
fi

# Check if the file exists
if [ ! -f "$1" ]
then
    echo "File not found!"
    exit 1
fi

# Extract the event types and count them
grep -o '^[0-9]*' "$1" | sort | uniq -c