#!/usr/bin/env sh
echo "Executing F3SlackUserLister"
date >> /Users/schaecher/PycharmProjects/PAXminer/PAXminer.log
./F3SlackUserLister.py
echo "Executing BDminer"
./BDminer.py
echo "Executing PAXminer"
./PAXminer.py