#!/bin/bash

echo "This script will deploy SlimbookBattery in your system (replacing previous installation if exists)"
echo "Press ENTER to proceed"
echo "CTRL-C to exit"
read

#Used python binary
python="python3"
python_pck_installer="pip3"
#Parse entire repository looking for python import string
python_packages=$(grep -Re "^import" * | awk '{print $2}' | sort -u)

echo "Checking Python dependencies..."
echo -ne "Dependencies are: $python $python_pck_installer"
python_packages=$python_packages
echo $python_packages

if [ ! $python ] && [ ! $python_pck_installer ];
then
	echo "Please install $python and $python_pck_installer"
	exit 1
else 
	for package in $python_packages; do
		if ! $($python -c "import $package" &> /dev/null);
		then
			echo "Installing \"$python_pck_installer $package\"..."
			if $python_pck_installer install $package; 
			then
				echo "... done"
			else
				echo "... ERROR: could not install $package. Try to install manually and run this script again"
				exit 1
			fi
		fi
	done  
fi

echo
echo "Check system dependencies..."
echo "TODO :')'"

echo "Removing previously installed resources..."
sudo rm -rf /usr/share/slimbookbattery/

echo
echo "Deploying..."
#TODO remove needed to create folder structure manually
sudo mkdir /usr/share/slimbookbattery
sudo mkdir /usr/share/slimbookbattery/images
sudo mkdir /usr/share/slimbookbattery/changelog
sudo mkdir /usr/share/slimbookbattery/src
sudo mkdir /usr/share/slimbookbattery/bin

while read line; do
	sudo cp -vrf $line
done < debian/install

echo
echo "Creating binary simlinks..."
sudo rm /usr/bin/slimbookbattery /usr/bin/slimbookbattery-pkexec
sudo cp -s /usr/share/slimbookbattery/bin/* /usr/bin/

echo
echo "Checking installation (post installation script)"
if ./src/check_config.py; then
	echo "Done!"
else
	echo "ERROR: See below otput, could not check your installation porperly"
fi
