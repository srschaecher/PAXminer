#!/usr/bin/env sh
echo "Executing PAXcharter"
cd /Users/schaecher/PycharmProjects/PAXminer/
date >> ./PAXminer.log
./PAXcharter.py
echo "Executing BDminer"
./BDminer.py
echo "Executing PAXminer"
./PAXminer.py