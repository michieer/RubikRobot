#!/bin/bash
folder='../tmp'

./take-photo.py $folder
./find-colors.py $folder
./solve-cube.py $folder
