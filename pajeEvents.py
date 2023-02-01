#!/usr/bin/python3
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates a sintetic PAJE trace file.')
    parser.add_argument('-n', '--number', help='Number of instructions to be processed.')

    args = parser.parse_args()

    
