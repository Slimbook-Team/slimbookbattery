#!/bin/bash

# This commands mustn't be executed as root
if command -v gnome-extensions;
    then
        gnome-extensions enable ubuntu-appindicators@ubuntu.com

        if [ $? -eq 2 ] ; then 
            exit 1
        fi

elif command -v gnome-shell-extension-tool;
    then
        gnome-shell-extension-tool -e ubuntu-appindicators@ubuntu.com
        if [ $? -eq 2 ] ; then 
            exit 1
        fi
else
    echo 'No program found'
fi

exit 0
