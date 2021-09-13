#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import configparser
import getpass
import os
import shutil
import subprocess

USER_NAME = getpass.getuser()
if USER_NAME == 'root':
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONF = os.path.join(CURRENT_PATH, 'slimbookbattery.conf')
CONFIG_FOLDER = os.path.join(HOMEDIR, '.config/slimbookbattery')
if not os.path.isdir(CONFIG_FOLDER):
    os.makedirs(CONFIG_FOLDER)
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'slimbookbattery.conf')


def main():
    check_config_file()
    check_tlp_files()
    if getpass.getuser() == 'root':
        print('Giving permisions ...')
        for dirpath, dirnames, filenames in os.walk(CONFIG_FOLDER):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                os.chmod(path, 0o777)
        print('Done')
    else:
        print('Done')


def check_config_file():
    print('Checking Slimbook Battery Configuration')
    if os.path.isfile(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        default_config = configparser.ConfigParser()
        default_config.read(DEFAULT_CONF)
        incidences = False

        for section in default_config.sections():
            print('Checking section: ' + section + '...')
            if not config.has_section(section):
                incidences = True
                config.add_section(section)
                print('Section added')

            for var in default_config.options(section):
                if not config.has_option(section, var):
                    incidences = True
                    print('Not found: ' + var)
                    config.set(section, var, default_config.get(section, var))

        if incidences:
            try:
                configfile = open(CONFIG_FILE, 'w')
                config.write(configfile)
                configfile.close()
                print('Incidences corrected.')
            except Exception:
                print('Incidences could not be corrected.')
        else:
            print('Incidences not found.')
    else:
        print('Creating config file ...')
        shutil.copy(DEFAULT_CONF, CONFIG_FILE)


def check_tlp_files():
    print("Checking Slimbook Battery's TLP Configuration")
    # Slimbookbattery tlp conf files

    files = ['ahorrodeenergia', 'equilibrado', 'maximorendimiento']

    # Checks if default files are the same in the app folder and in the system,
    # if something changed all will be restored
    for file in files:
        incidences = False
        home_file = os.path.join(CONFIG_FOLDER, file)
        usr_file = os.path.join(CURRENT_PATH, '../custom', file)

        if os.path.isfile(home_file):
            print('Found ' + file)
            if subprocess.getstatusoutput('diff {} {}'.format(usr_file, home_file)) != 0:
                incidences = True
        else:
            incidences = True

        if incidences:
            print('Setting default an custom files ...')
            if os.path.isfile(usr_file):
                shutil.copy(usr_file, home_file)
            else:
                default_file = os.path.join(CURRENT_PATH, '../default', file)
                if os.path.isfile(default_file):
                    shutil.copy(default_file, home_file)


if __name__ == '__main__':
    print('Config check executed as ' + USER_NAME)
    main()
