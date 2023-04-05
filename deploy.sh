#!/bin/bash

###############################################################################

# Prepare terminal output formatting.

INFO=""
WARN=""
DONE=""
BOLD=""
RESET=""

if [[ $(command -v tput) ]]; then
	INFO=$(tput setaf 3)
	WARN=$(tput setaf 1)
	DONE=$(tput setaf 2)
	BOLD=$(tput bold)
	RESET=$(tput sgr0)
fi


print_info()
{
	echo -e $INFO"$@"$RESET
}


print_info_bold()
{
	echo -e $INFO$BOLD"$@"$RESET
}


print_warn()
{
	echo -e $WARN"$@"$RESET
}


print_warn_bold()
{
	echo -e $WARN$BOLD"$@"$RESET
}


print_done()
{
	echo -e $DONE"$@"$RESET
}


print_done_bold()
{
	echo -e $DONE$BOLD"$@"$RESET
}


print_bold()
{
	echo -e $BOLD"$@"$RESET
}

###############################################################################

# Visible execution starts here.

# Must be run as root.
if [ "$EUID" -ne 0 ]; then
	print_warn_bold "ERROR: Please run this script as root."
	exit 1
fi

print_info_bold "
This script will install SlimbookBattery in your system (replacing previous
installation if exists).
Press ENTER to proceed, or CTRL-C to exit.
"

read

###############################################################################

# Install dependencies - both system and Python.

# Check for Python (pip is generally installed automatically).
if [[ ! $(command -v python3) ]]; then
	print_warn_bold "Please install Python 3."
	exit 1
elif [[ ! $(command -v pip3) ]]; then
	print_warn_bold "Please install pip3."
	exit 1
fi


# This will be extended later depending on distro. Hence the trailing space.
system_dependencies="tlp tlp-rdw libnotify-bin cron gobject-introspection "
pkg_mgr_found="true"

if [[ $(command -v apt-get) ]]; then
	# Debian based distro.
	system_dependencies+="libayatana-appindicator3-1"
	pkg_install_cmd="apt-get install -y"
	pkg_search_cmd="dpkg-query -l"

elif [[ $(command -v pacman) ]]; then
	# Arch based distro.
	system_dependencies+="libindicator-gtk3 libappindicator-gtk3"
	pkg_install_cmd="pacman -S"
	pkg_search_cmd="pacman -Qs"

elif [[ $(command -v yum) ]]; then
	# RPM based distro.
	system_dependencies+="libindicator-gtk3 libappindicator-gtk3"
	pkg_install_cmd="yum install"
	pkg_search_cmd="yum list installed | grep"

else
	pkg_mgr_found="false"
	print_info_bold "Cannot find a supported package manager." \
			"\nAssuming the required dependencies are installed." \
			"\nPress ENTER to proceed, or CTRL-C to exit."
	read

fi


if [[ $pkg_mgr_found == "true" ]]; then
	print_info_bold "Checking and installing the following system" \
			"dependencies (if needed)..."
	print_info "$system_dependencies\n"

	for pkg in $system_dependencies; do
		eval "$pkg_search_cmd $pkg >/dev/null 2>&1"
		if [[ $? -ne 0 ]]; then
			print_info "Trying to install $pkg..."
			eval "$pkg_install_cmd $pkg >/dev/null 2>&1"
			if [[ $? -eq 0 ]]; then
				print_done "...Done installing $pkg!"
			else
				print_warn_bold "ERROR: Could not install" \
						"$pkg. Please install it" \
						"manually."
				exit 1
			fi
		fi
	done

	print_info_bold "...Done installing system dependencies!\n"
fi


print_info_bold "Installing Python dependencies..."

if [[ ! $(pip3 install -r requirements.txt) ]]; then
	print_warn_bold "ERROR: Could not install Python dependencies."
	exit 1
fi

print_info_bold "...Done installing Python dependencies!\n"

###############################################################################

# The main installation starts here. Will exit on failure.

print_info_bold "Installing SlimbookBattery...\n"
set -e

print_info "Removing previously installed resources..."
rm -rf /usr/bin/slimbookbattery*
rm -rf /usr/share/slimbookbattery/
print_info "...Done removing previously installed resources!\n"


# TODO: Remove the need to create folder structure manually.
print_info "Creating folder structure..."
mkdir /usr/share/slimbookbattery
mkdir /usr/share/slimbookbattery/bin
mkdir /usr/share/slimbookbattery/custom
mkdir /usr/share/slimbookbattery/default
mkdir /usr/share/slimbookbattery/images
mkdir /usr/share/slimbookbattery/src
print_info "...Done creating folder structure!\n"


print_info "Copying contents..."
while read line; do
	cp -vrf $line
done < debian/install
print_info "...Done copying contents!\n"


print_info "Creating binary symlinks..."
rm /usr/bin/slimbookbattery /usr/bin/slimbookbattery-pkexec
cp -sv /usr/share/slimbookbattery/bin/* /usr/bin/
chmod +x /usr/share/slimbookbattery/bin/*
print_info "...Done creating binary symlinks!\n"


print_info_bold "Running post installation script and applying translations..."
chmod +x debian/postinst

if [[ $(./src/check_config.py && ./debian/postinst) ]]; then
	print_done_bold "...Done installing SlimbookBattery!"
else
	print_warn_bold "ERROR: See the output, could not check your" \
			"installation porperly"
	exit 1
fi

###############################################################################
