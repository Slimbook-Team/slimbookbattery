#!/bin/bash
# This file must be executed inside src

programa='slimbookbatterypreferences'

# 1. Generating .pot / .po

pygettext3 -d $programa $programa.py

eval "mv $programa.pot ./locale/$program.template.po"

