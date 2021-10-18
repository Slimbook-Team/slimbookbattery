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
#system_dependencies="libindicator7 libappindicator1 gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0 gir1.2-glib-2.0 libappindicator3-1 libgirepository-1.0-1 gir1.2-notify-0.7 gir1.2-appindicator3-0.1 tlp tlp-rdw libnotify-bin cron"
echo "TODO..."
for lib in $system_dependencies; do
	if ! $(whereis $lib &> /dev/null);
	then
		echo "Missing package: $lib. Try to install using your distro package manager"
		exit 1
	fi
done

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
sudo cp -sv /usr/share/slimbookbattery/bin/* /usr/bin/

echo
echo "Checking installation (post installation script and applying translations)"
chmod +x debian/postinst
if ./src/check_config.py && ./debian/postinst && ./replace.sh ; then
	echo "Done!"
	exit 0
else
	echo "ERROR: See below otput, could not check your installation porperly"
	exit 1
fi
