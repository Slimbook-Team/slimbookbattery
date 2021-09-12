#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import configparser
import os
import subprocess
import sys

USERNAME = subprocess.getstatusoutput("logname")

if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd ' + USERNAME[1]) == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = subprocess.getoutput("echo ~" + USER_NAME)

CURRPATH = os.path.dirname(os.path.realpath(__file__))

default = CURRPATH + '/slimbookbattery.conf'
config_file = HOMEDIR + '/.config/slimbookbattery/slimbookbattery.conf'

print('Config check executed as ' + USER_NAME)


def main(args):
    check()
    check2()
    if subprocess.getoutput('whoami') == 'root':
        print('Giving permisions ...')
        os.system('sudo chmod 777 -R ' + HOMEDIR + '/.config/slimbookbattery')
        print('Done')
    else:
        print('Done')


def check():  # Args will be like --> command_name value
    print('Checking Slimbook Battery Configuration')
    if os.path.isfile(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        default_config = configparser.ConfigParser()
        default_config.read(default)
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
                    config.set(section, var, config.get(section, var))

        if incidences:
            try:
                configfile = open(config_file, 'w')
                config.write(configfile)
                configfile.close()
                print('Incidences corrected.')
            except Exception:
                print('Incidences could not be corrected.')
        else:
            print('Incidences not found.')
    else:
        print('Creating config file ...')
        os.system('''mkdir -p ''' + HOMEDIR + '''/.config/slimbookbattery/ && cp ''' + default + ''' ''' + config_file)


def check2():
    print("Checking Slimbook Battery's TLP Configuration")
    # Slimbookbattery tlp conf files
    incidences = False

    files = ['ahorrodeenergia', 'equilibrado', 'maximorendimiento']

    # Checks if default files are the same in the app folder and in the system,
    # if something changed all will be restored
    for file in files:
        if os.path.isfile(HOMEDIR + '/.config/slimbookbattery/default/' + file):
            print('Found ' + file)
            usr_file = os.path.join('/usr/share/slimbookbattery/custom/', file)
            home_file = os.path.join(HOMEDIR, '.config/slimbookbattery', file)

            if subprocess.getstatusoutput('diff {} {}'.format(usr_file, home_file)) != 0:
                incidences = True
        else:
            incidences = True

    if incidences:
        print('Setting default an custom files ...')
        os.system('''cp -r /usr/share/slimbookbattery/custom ''' + HOMEDIR + '''/.config/slimbookbattery/
                    cp -r /usr/share/slimbookbattery/default ''' + HOMEDIR + '''/.config/slimbookbattery/
                    ''')


main(sys.argv)
