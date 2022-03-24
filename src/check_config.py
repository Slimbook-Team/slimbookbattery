#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import configparser
import logging
import os
import pwd
import shutil
import subprocess
import sys

# We want load first current location
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
if CURRENT_PATH not in sys.path:
    sys.path = [CURRENT_PATH] + sys.path
import utils

USER_NAME = utils.get_user()

HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONF = os.path.join(CURRENT_PATH,'configuration', 'slimbookbattery.conf')
CONFIG_FOLDER = os.path.join(HOMEDIR, '.config/slimbookbattery')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'slimbookbattery.conf')

UPDATES_DIR = os.path.join(CURRENT_PATH, 'updates')

uid, gid = pwd.getpwnam(USER_NAME).pw_uid, pwd.getpwnam(USER_NAME).pw_gid

logger = logging.getLogger()


def main():
    if not os.path.isdir(CONFIG_FOLDER):
        logger.info('Creating config folder ...')
        os.umask(0)
        os.makedirs(CONFIG_FOLDER, mode=0o766)  # creates with perms
        os.chown(CONFIG_FOLDER, uid, gid)  # set user:group
        logger.info(subprocess.getoutput('ls -la ' + CONFIG_FOLDER))
    else:
        logger.info('Configuration folder ({}) found!'.format(CONFIG_FOLDER))

    set_ownership(CONFIG_FOLDER)
    set_ownership(UPDATES_DIR)

    check_config_file()
    check_tlp_files()

def set_ownership(folder):
    folder_stat = os.stat(folder)
    logger.debug("Folder {}\nUser uid={}\nFolder uid={}".format(folder, uid, folder_stat.st_uid))
    f_uid = folder_stat.st_uid
    f_gid = folder_stat.st_gid

    if not uid == f_uid or not gid == f_gid:
        #logger.info('Setting {} ownership').format(folder)

        for dir_path, dir_name, filenames in os.walk(folder):
            logger.debug(dir_path)
            os.chown(dir_path, uid, gid)
            for filename in filenames:
                file_path = os.path.join(dir_path, filename)
                logger.debug(file_path)
                os.chown(file_path, uid, gid)

def check_config_file():
    logger.info('Checking Slimbook Battery Configuration')
    if os.path.isfile(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        default_config = configparser.ConfigParser()
        default_config.read(DEFAULT_CONF)
        incidences = False

        for section in default_config.sections():
            logger.info('Checking section: {} ...'.format(section))
            if not config.has_section(section):
                incidences = True
                config.add_section(section)
                logger.info('Section added')

            for var in default_config.options(section):
                if not config.has_option(section, var):
                    incidences = True
                    logger.info('Not found: {}'.format(var))
                    config.set(section, var, default_config.get(section, var))

        if incidences:
            try:
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
                logger.info('Incidences corrected.')
            except Exception:
                logger.exception('Incidences could not be corrected.')
        else:
            logger.info('Incidences not found.')

    else:
        logger.info('Creating config file ...')
        shutil.copy(DEFAULT_CONF, CONFIG_FOLDER)
        os.chown(CONFIG_FILE, uid, gid)  # set user:group


# Checks if the user's default config files exist an if they are like the app version's default files.
# If files or directories don't exist they are created.
def check_tlp_files():
    logger.info("Checking Slimbook Battery's TLP Configuration")

    incidences = False
    usr_custom_dir = os.path.join(CONFIG_FOLDER, 'custom/')
    usr_default_dir = os.path.join(CONFIG_FOLDER, 'default/')
    app_default_dir = os.path.join(CURRENT_PATH, '../default/')

    files = ['ahorrodeenergia', 'equilibrado', 'maximorendimiento']

    # Checks if default files are the same in the app folder and in the system,
    # if something changed all will be restored
    for file in files:

        app_default_file = os.path.join(usr_default_dir, file)
        usr_default_file = os.path.join(usr_default_dir, file)

        # If user default is different from app default -- updates
        if os.path.isfile(usr_default_file) and os.path.isfile(app_default_file):
            logger.info('Checking {}'.format(file))
            if subprocess.getstatusoutput('diff {} {}'.format(app_default_dir, usr_default_dir))[0] != 0:
                logger.info('Default files have changed, updating:')
                incidences = True
        else:
            logger.info('{} does not exist.'.format(usr_default_file))
            incidences = True

    if incidences:
        logger.info('Resetting default and custom files ...')

        if os.path.isdir(app_default_dir):
            if not (os.path.isdir(usr_default_dir) and os.path.isdir(usr_custom_dir)):
                logger.info('Creating directories')
                os.makedirs(usr_default_dir, mode=0o766)
                os.chown(usr_default_dir, uid, gid)  # set user:group
                os.mkdir(usr_custom_dir, mode=0o766)
                os.chown(usr_custom_dir, uid, gid)  # set user:group

            for file in files:
                app_default_file = os.path.join(app_default_dir, file)
                shutil.copy(app_default_file, usr_default_dir)
                shutil.copy(app_default_file, usr_custom_dir)
                os.chown(os.path.join(usr_default_dir, file), uid, gid)  # set user:group
                os.chown(os.path.join(usr_custom_dir, file), uid, gid)  # set user:group
        else:
            logger.error('Base default file not found')
    else:
        logger.info('Incidences not found.')


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info('Config check executed as {}'.format(USER_NAME))
    main()
