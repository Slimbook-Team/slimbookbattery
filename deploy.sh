#!/bin/bash

echo "This script will deploy SlimbookBattery in your system (replacing previous installation if exists)"
echo "Press ENTER to proceed"
echo "CTRL-C to exit"
read

echo "Removing previously installed resources..."
sudo rm -rf /usr/share/slimbookbattery/*
sudo rm /usr/bin/slimbookbattery /usr/bin/slimbookbattery-pkexec

echo "Deploying..."
sudo mkdir /usr/share/slimbookbattery
sudo cp -vRf . /usr/share/slimbookbattery/

sudo cp -s /usr/share/slimbookbattery/bin/* /usr/bin/
