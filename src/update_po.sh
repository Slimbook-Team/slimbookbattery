#!/bin/bash
# This file must be executed inside src
set -x
programas=$(ls ./*.py)

# 1. Generating .pot / .po
for programa in *.py
do
    cat $programa | grep 'import gettext'
    if [ $? -eq 0 ]; then
        programa=$(echo $programa | cut -d'.' -f1)
        echo $programa
        pygettext3 -d $programa $programa.py
        if [ $? -eq 0 ]; then
            eval "mv $programa.pot ./locale/$programa.template.po"
            echo Done
        else
            echo 'Not done'
        fi
    fi
done