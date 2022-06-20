#!/bin/bash
# This file must be executed inside src
set -x
programas=$(ls ./../../src/*.py)

cd ./../../src
# 1. Generating .pot / .po
for programa in *.py
do
    echo $programa
    cat $programa | grep '_ = utils.load_translation'
    if [ $? -eq 0 ]; then
        programa=$(echo $programa | cut -d'.' -f1)
        echo $programa
        pygettext3 -d $programa $programa.py
        if [ $? -eq 0 ]; then
            eval "mv $programa.pot ./translations/$programa.template.po"
            echo Done
        else
            echo 'Not done'
        fi
    fi
done