#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import configparser
import getpass
import os
import pwd
import shutil
import subprocess

USER_NAME = getpass.getuser()
if USER_NAME == 'root':
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONF = os.path.join(CURRENT_PATH, 'slimbookbattery.conf')
CONFIG_FOLDER = os.path.join(HOMEDIR, '.config/slimbookbattery')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'slimbookbattery.conf')

uid, gid =  pwd.getpwnam(USER_NAME).pw_uid, pwd.getpwnam(USER_NAME).pw_gid

def main():    


    if not (os.path.isdir(CONFIG_FOLDER) == True):
        print('Creating config folder ...')
        os.umask(0)
        os.makedirs(CONFIG_FOLDER, mode=0o766) # creates with perms 
        os.chown(CONFIG_FOLDER, uid, gid) # set user:group 
        print(subprocess.getoutput('ls -la '+CONFIG_FOLDER))
    else:
        print('Configuration folder ('+CONFIG_FOLDER+') found!')

    check_config_file()
    check_tlp_files()

    


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
        shutil.copy(DEFAULT_CONF, CONFIG_FOLDER)



# Checks if the user's default config files exist an if they are like the app version's default files.
# If files or directories don't exist they are created. 
def check_tlp_files():
    print("\nChecking Slimbook Battery's TLP Configuration")
    
    incidences = False
    usr_custom_dir = os.path.join(CONFIG_FOLDER,'custom/')
    usr_default_dir = os.path.join(CONFIG_FOLDER,'default/')
    app_default_dir = os.path.join(CURRENT_PATH, '../default/')

    files = ['ahorrodeenergia', 'equilibrado', 'maximorendimiento']

    # Checks if default files are the same in the app folder and in the system,
    # if something changed all will be restored
    for file in files:

        app_default_file = os.path.join(usr_default_dir, file)
        usr_default_file = os.path.join(usr_default_dir, file)

        # If user default is different from app default -- updates
        if os.path.isfile(usr_default_file) and os.path.isfile(app_default_file):
            print('\n\tChecking ' + file)
            if subprocess.getstatusoutput('diff {} {}'.format(app_default_dir, usr_default_dir))[0] != 0:
                print('\tDefault files have changed, updating:')
                incidences = True
        else:
            print('\n' + usr_default_file + ' does not exist.')
            incidences = True

    if incidences:
        print('\nResetting default and custom files ...')
        
        if os.path.isdir(app_default_dir):

            if not (os.path.isdir(usr_default_dir) and os.path.isdir(usr_custom_dir)):       
                    print('Creating directories')
                    os.makedirs(usr_default_dir, mode=0o766)
                    os.chown(usr_default_dir, uid, gid) # set user:group 
                    os.mkdir(usr_custom_dir, mode=0o766)
                    os.chown(usr_custom_dir, uid, gid) # set user:group 
 
            for file in files:
                app_default_file = os.path.join(app_default_dir, file)
                shutil.copy(app_default_file, usr_default_dir)
                shutil.copy(app_default_file, usr_custom_dir)
       
        else:
            print('Base default file not found')
    else:
        print('\n\tIncidences not found.')


if __name__ == '__main__':
    print('Config check executed as ' + USER_NAME)
    main()
