#!/bin/bash

# This commands mustn't be executed as root
if command -v gnome-extensions;
    then
        gnome-extensions enable ubuntu-appindicators@ubuntu.com
elif command -v gnome-shell-extension-tool;
    then
        gnome-shell-extension-tool -e ubuntu-appindicators@ubuntu.com
else
    echo 'No program found'
fi