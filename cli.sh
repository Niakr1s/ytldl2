#!/usr/bin/env bash

# This is an example scrypt to use with your library

if [ -z "$1" ]; then
        echo "provide password"
        exit 1
fi

cwd=~/projects/ytldl2
dir="/data/hdd1/!YT"

$cwd/.venv/bin/python $cwd/cli.py -d $dir -p "$1"
