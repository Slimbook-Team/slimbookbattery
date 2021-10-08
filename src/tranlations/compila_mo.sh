#!/bin/bash
# This file must be executed inside locale
# 1. Removing .mo
for archivo in ./*/LC_MESSAGES/*.mo
do
{ # try

    rm $archivo
    #save your output

} || { # catch
    # save log for exception 
    echo No .mo files
}
done

# 2. Compiling .mo 
for archivo in ./*/LC_MESSAGES/*.po
do
echo msgfmt $archivo -o .$(echo $archivo | cut -d'.' -f2).mo
msgfmt $archivo -o .$(echo $archivo | cut -d'.' -f2).mo
done