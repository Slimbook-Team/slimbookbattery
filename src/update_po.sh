#!/bin/bash
# This file must be executed inside src
set -x
programa='slimbookbatteryindicator'

# 1. Generating .pot / .po

pygettext3 -d $programa $programa.py
if [ $? -eq 0 ]; then
    eval "mv $programa.pot ./locale/$programa.template.po"
    echo Done
else
    echo 'Not done'
fi
