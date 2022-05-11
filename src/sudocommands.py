#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Slimbook Battery
# Copyright (C) 2021 Slimbook
# In case you modify or redistribute this code you must keep the copyright line above.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# This file will be executed as sudo by pkexec
import logging
import os
import pwd
import re
import shutil
import subprocess
import sys
from configparser import ConfigParser

# We want load first current location
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
if CURRENT_PATH not in sys.path:
    sys.path = [CURRENT_PATH] + sys.path
import utils
USER_NAME = utils.get_user()
HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

TLP_CONF = utils.get_tlp_conf_file()[0]
print('Using ', TLP_CONF)

def get_logger(logger_name, create_file=False):

        log = logging.getLogger(logger_name)
        log.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')

        if create_file:
            try:            
                fh = logging.FileHandler('/var/log/slimbookbattery.log')
            except PermissionError:
                log.critical(
                    'Cannot open log file /var/slimbookbattery.log, using /tmp/slimbookbattery.log')
                fh = logging.FileHandler('/tmp/slimbookbattery.log')
            if fh:
                fh.setLevel(level=logging.ERROR)
                fh.setFormatter(formatter)

            log.addHandler(fh)

        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(level=logging.DEBUG)
        ch.setFormatter(formatter)
        log.addHandler(ch)
        return log 

logger = get_logger(USER_NAME, True)

logger.debug('******************************************************************************')

logger.info('\x1b[6;30;42mSlimbookBattery-Commandline, executed as: {}\x1b[0m'.format(USER_NAME))

logger.debug("Username: {} - Homedir: {}".format(USER_NAME, HOMEDIR))

config_file = os.path.join(HOMEDIR, '.config/slimbookbattery/slimbookbattery.conf')
config = ConfigParser()
config.read(config_file)

_ = utils.load_translation('sudocommands')

msg_graphics = _('Graphics settings have been modified, changes will be applied on restart.')

class Colors:  # You may need to change color settings
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    CYAN = "\033[1;36m"
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    BOLD = "\033[;1m"

MAPPING_MODES = {
    '1': {
        'full_text': 'Power saving mode',
        'mode_name': 'ahorrodeenergia',
        'tdp_mode': 'low',
        'graphics_check': 'graphics_ahorro',
        'graphics_profile': 'low',
        'graphics_limit': (0, 600, 600, 800),
        'brightness_setting_check': 'saving_brightness_switch',
        'brightness_setting_value': 'ahorro_brightness',
    },
    '2': {
        'full_text': 'Normal power mode',
        'mode_name': 'equilibrado',
        'tdp_mode': 'medium',
        'graphics_check': 'graphics_equilibrado',
        'graphics_profile': 'mid',
        'graphics_limit': (0, 600, 900, 1000),
        'brightness_setting_check': 'balanced_brightness_switch',
        'brightness_setting_value': 'equilibrado_brightness',
    },
    '3': {
        'full_text': 'Full power mode',
        'mode_name': 'maximorendimiento',
        'tdp_mode': 'high',
        'graphics_check': 'graphics_maxrendimiento',
        'graphics_profile': 'high',
        'graphics_limit': (0, 600, 900, 1000),
        'brightness_setting_check': 'power_brightness_switch',
        'brightness_setting_value': 'maxrendimiento_brightness',
    },
}


def main(args):  # Args will be like --> command_name value

    arguments = ''
    for argument in range(len(args)):
        if argument != 0:
            arguments = arguments + ' ' + (args[argument])
    logger.debug("Arguments: {}".format(arguments))

    if (len(args)) > 1:

        battery_mode = config.get('CONFIGURATION', 'modo_actual')

        if args[1] == "apply":  # Applies selected mode conf and turns on/off tlp
            brightness_settings(battery_mode)
            required_reboot = mode_settings(battery_mode)
            
            if required_reboot == 1:
                logger.info('Sudo notify')
                notify(msg_graphics)

            exit(required_reboot)

        if args[1] == "restore":

            logger.info("Resetting modes conf")
            modes = ('ahorrodeenergia', 'equilibrado', 'maximorendimiento')

            uid, gid = None, None
            try:
                pwnam = pwd.getpwnam(USER_NAME)
                uid, gid = pwnam.pw_uid, pwnam.pw_gid
            except Exception:
                logger.error('Failed to get user id/gid: {}'.format(USER_NAME))
                exit(5)

            for mode in modes:
                custom_file = os.path.join(HOMEDIR, ".config/slimbookbattery/custom/", mode)
                default_file = os.path.join(HOMEDIR, ".config/slimbookbattery/default/", mode)

                os.remove(custom_file)
                shutil.copy(default_file, custom_file)
                os.chown(custom_file, uid, gid)  # set user:group

            # Slimbook Battery Configuration
            logger.info("Resetting Slimbook Battery's conf")
            custom_file = os.path.join(HOMEDIR, ".config/slimbookbattery/slimbookbattery.conf")
            default_file = os.path.join(CURRENT_PATH, "configuration", "slimbookbattery.conf")
            logger.info(default_file)

            os.remove(custom_file)
            shutil.copy(default_file, custom_file)
            os.chown(custom_file, uid, gid)  # set user:group

        if args[1] == "autostart":  # Sets brightness and enables tdp
            battery_mode = config.get('CONFIGURATION', 'modo_actual')
            brightness_settings(battery_mode)

        if args[1] == "report":
            os.system(
                "sudo python3 " + CURRENT_PATH + "/slimbookbattery-report.py " + args[2] + ' ' + args[3] + ' ' + args[
                    4])

        if args[1] == "restart_tlp":
            logger.info('Restarting TLP...')
            os.system("sudo tlp start")

        if args[1] == "service":  # Manages slimbookbattery.service
            if args[2] == "start":
                os.system('sudo systemctl start slimbookbattery.service')

            elif args[2] == "restart":
                os.system('sudo systemctl restart slimbookbattery.service')

            elif args[2] == "stop":
                os.system('sudo systemctl stop slimbookbattery.service')

            elif args[2] == "create":
                os.system(
                    'sudo cp /usr/share/slimbookbattery/src/service/slimbookbattery.service '
                    '/lib/systemd/system/slimbookbattery.service')
                os.system('sudo chmod 755 /usr/share/slimbookbattery/src/service/slimbookbatteryservice.sh')
                os.system('systemctl daemon-reload')

        if args[1] == "change_config":
            change_config(args)

    logger.debug('******************************************************************************')


def notify(msg):
    os.system('''set -x
                display=":$(ls /tmp/.X11-unix/* | sed 's#/tmp/.X11-unix/X##' | head -n 1)"
                user=''' + USER_NAME + '''
                uid=$(id -u $user)
                sudo -u $user DISPLAY=$display DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$uid/bus notify-send "Slimbook Battery" "''' + msg + '''"
                ''')


def change_config(args):  # For general page options
    logger.info('\n{}[CHANGE CONFIGURATION]{}'.format(Colors.GREEN, Colors.ENDC))
    files = [TLP_CONF,
             os.path.join(HOMEDIR, '.config/slimbookbattery/custom/ahorrodeenergia'),
             os.path.join(HOMEDIR, '.config/slimbookbattery/custom/equilibrado'),
             os.path.join(HOMEDIR, '.config/slimbookbattery/custom/maximorendimiento')]

    for filepath in files:
        update_config(filepath, args[2], args[3])


def mode_settings(mode):
    required_reboot = 0
    logger.info('\n{}[MODE SETTINGS]{}'.format(Colors.GREEN, Colors.ENDC))

    graficaNvidia = False
    graphics_before = ''

    # Checking graphics
    stout = subprocess.getstatusoutput('prime-select query')
    print('Checking graphics...')
    # nvidia = subprocess.getstatusoutput("prime-select " + stout + "| grep -i 'profile is already set'")
    if stout[0] == 0:  #
        graficaNvidia = True
        graphics_before = stout

    print(stout)

    # If nvidia driver is not installed or does not work, we use TLP
    if not graficaNvidia:
        logger.info('Setting graphics frequency ...')

        if mode in MAPPING_MODES:
            variable = MAPPING_MODES[mode]['graphics_check']
            profile = MAPPING_MODES[mode]['graphics_profile']
            limit = MAPPING_MODES[mode]['graphics_limit']
            mode_name = MAPPING_MODES[mode]['mode_name']
            filepath = os.path.join(HOMEDIR, '.config/slimbookbattery/custom', mode_name)
        else:
            logger.error('Mode must be {}, found: {}'.format(MAPPING_MODES.keys(), mode))
            return -1

        # GRAPHICS AMD SETTINGS de
        RADEON_POWER_PROFILE_ON_BAT = 'default'
        RADEON_DPM_STATE_ON_BAT = 'battery'
        RADEON_DPM_PERF_LEVEL_ON_BAT = 'auto'

        # RADEON
        if subprocess.getstatusoutput('lscpu | grep -i model | grep  -i Radeon')[0] == 0:
            logger.info('Radeon graphics power profile: {}'.format(profile))
            if config.getboolean('SETTINGS', variable):
                RADEON_POWER_PROFILE_ON_BAT = profile

            os.system(
                'sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ cRADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                    RADEON_POWER_PROFILE_ON_BAT, filepath
                )
            )
            os.system(
                'sed -i "/RADEON_DPM_STATE_ON_BAT=/ cRADEON_DPM_STATE_ON_BAT={}" {}'.format(
                    RADEON_DPM_STATE_ON_BAT, filepath
                )
            )
            os.system(
                'sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ cRADEON_DPM_PERF_LEVEL_ON_BAT={}" {}'.format(
                    RADEON_DPM_PERF_LEVEL_ON_BAT, filepath
                )
            )
        # INTEL
        elif subprocess.getstatusoutput('lspci | grep VGA | grep -i Intel')[0] == 0:
            # GRAPHICS INTEL SETTINGS
            freq_table = ''
            freq_available = ''
            freqCorrecta = True

            min_bat = 0
            min_ac = 0

            max_bat = 0
            max_ac = 0

            boost_bat = 0
            boost_ac = 0

            if os.path.isfile('/sys/kernel/debug/dri/0/i915_ring_freq_table'):
                freq_table = subprocess.getoutput('cat /sys/kernel/debug/dri/0/i915_ring_freq_table')
                freq_table = freq_table.split('\n')
                freq_table.pop(0)
                freq_available = ''

                for i in freq_table:
                    valor = i.split()
                    freq_available = freq_available + ' ' + valor[0]

                freq_available = freq_available.strip().split(' ')
                logger.info('Available frequencies: {}'.format(freq_available))

            # FRECUENCIAS PARA LOS MODOS
            if not len(freq_available) > 1:
                freqCorrecta = False

            logger.info('Intel graphics power profile: {}'.format(profile))
            if config.getboolean('SETTINGS', variable):
                # MIN_BAT/MIN_AC
                for i in range(len(freq_available)):
                    if (int(freq_available[i]) > limit[0] and int(freq_available[i]) < limit[1]):
                        min_bat = int(freq_available[i])
                        min_ac = int(freq_available[i])
                        break

                # Si el valor que se busca no se encuentra, el boolean freqCorrecta pasará a False y
                # por lo tanto no se realizará ninguna modificación respecto a gráficas Intel
                if min_bat == 0 or min_ac == 0:
                    freqCorrecta = False

                # MAX_BAT/MAX_AC
                if freqCorrecta:
                    for i in range(len(freq_available)):

                        if (int(freq_available[i]) >= limit[2] and int(freq_available[i]) < limit[3]):
                            max_bat = int(freq_available[i])
                            break

                    if int(freq_available[-1]) > 0:
                        max_ac = int(freq_available[-1])

                    if max_bat == 0 or max_ac == 0:
                        freqCorrecta = False

                # BOOST_BAT/BOOST_AC
                if freqCorrecta:
                    for i in range(len(freq_available)):

                        if (int(freq_available[i]) >= limit[3] and int(freq_available[i]) < int(freq_available[-1])):
                            boost_bat = int(freq_available[i])
                            break

                    if int(freq_available[-1]) > 0 and freqCorrecta:
                        boost_ac = int(freq_available[-1])

                    if boost_bat == 0 or boost_ac == 0:
                        freqCorrecta = False

                # Si el boolean sigue en True querrá decir que se han obtenido valores para min, max y boost
                if freqCorrecta:
                    logger.info('Setting GPU frequencies on bat --> {} {} {}'.format(
                        str(min_bat), str(max_bat), str(boost_bat))
                    )
                    update_config(filepath, 'INTEL_GPU_MIN_FREQ_ON_BAT', str(min_bat))
                    update_config(filepath, 'INTEL_GPU_MIN_FREQ_ON_AC', str(min_ac))
                    update_config(filepath, 'INTEL_GPU_MAX_FREQ_ON_BAT', str(max_bat))
                    update_config(filepath, 'INTEL_GPU_MAX_FREQ_ON_AC', str(max_ac))
                    update_config(filepath, 'INTEL_GPU_BOOST_FREQ_ON_BAT', str(boost_bat))
                    update_config(filepath, 'INTEL_GPU_BOOST_FREQ_ON_AC', str(boost_ac))
                else:
                    logger.info('Frequency not changed')
            else:
                logger.info('Intel graphics power profile: #{}'.format(profile))
                os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_BAT=/ c#INTEL_GPU_MIN_FREQ_ON_BAT=0" ' + filepath)
                os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_AC=/ c#INTEL_GPU_MIN_FREQ_ON_AC=0" ' + filepath)
                os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_BAT=/ c#INTEL_GPU_MAX_FREQ_ON_BAT=0" ' + filepath)
                os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_AC=/ c#INTEL_GPU_MAX_FREQ_ON_AC=0" ' + filepath)
                os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_BAT=/ c#INTEL_GPU_BOOST_FREQ_ON_BAT=0" ' + filepath)
                os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_AC=/ c#INTEL_GPU_BOOST_FREQ_ON_AC=0" ' + filepath)
        else:
            logger.error('Graphics 404')
    
    mode_name = ''
    # Copies selected custom mode conf to TLP_CONF
    # print('Passing Custom Configuration '+battery_mode+' to tlp.conf')
    if mode in MAPPING_MODES:
        logger.info(MAPPING_MODES[mode]['full_text'])
        mode_name = MAPPING_MODES[mode]['mode_name']

    logger.info("\n{}[COPY TLP CUSTOM SETTINGS]{}".format(Colors.GREEN, Colors.ENDC))
    custom_file = os.path.join(HOMEDIR, ".config/slimbookbattery/custom/", mode_name)
    exit_code, msg = subprocess.getstatusoutput("sudo cp {} {}".format(custom_file, TLP_CONF))
    if exit_code == 0:
        logger.info('File copied succesfully!')
    else:
        logger.error('Execution failed {}'.format(msg))

    # Sets mode changes and enables/disables TLP according to conf
    if config.getboolean('CONFIGURATION', 'application_on'):
        application_on = '1'
    else:  # Disablig TLP in conf
        application_on = '0'
    if update_config(TLP_CONF, 'TLP_ENABLE', application_on) == 0:
        logger.info('\nTLP Status = {}'.format(application_on))

    # Restarting TLP
    subprocess.getoutput("sudo tlp start")
    
    # If nvidia driver is installed and works WE SET IT MANUALLY
            
    if graficaNvidia:
        logger.info('Detected nvidia graphics profile: {}'.format(graphics_before))
        logger.info('Setting new profile ...')
        if mode == '1':

            if config.getboolean('SETTINGS', 'graphics_ahorro') and graphics_before != 'intel':
                if not graphics_before == 'intel':
                    os.system('prime-select intel')

            elif not config.getboolean('SETTINGS', 'graphics_ahorro') and graphics_before != 'on-demand':
                if not graphics_before == 'on-demand':
                    os.system('prime-select intel')
                    # avocado
                    os.system('prime-select on-demand')

        elif mode == '2':

            if config.getboolean('SETTINGS', 'graphics_equilibrado') and graphics_before != 'on-demand':
                if not graphics_before == 'on-demand':
                    os.system('prime-select intel')
                    os.system('prime-select on-demand')

            elif not config.getboolean('SETTINGS', 'graphics_equilibrado') and graphics_before != 'nvidia':
                if not graphics_before == 'nvidia':
                    os.system('prime-select nvidia')

        elif mode == '3':  # need to check
            if config.getboolean('SETTINGS', 'graphics_maxrendimiento') and graphics_before != 'on-demand':
                if not graphics_before == 'on-demand':
                    os.system('prime-select intel')
                    os.system('prime-select on-demand')

            elif not config.getboolean('SETTINGS', 'graphics_maxrendimiento') and graphics_before != 'nvidia':
                if not graphics_before == 'nvidia':
                    os.system('prime-select nvidia')

        graphics_after = subprocess.getoutput('prime-select query')
        logger.debug('Graphics before --> {} // Graphics after --> {}'.format(graphics_before, graphics_after))
        if not graphics_before == graphics_after:
            logger.info('Required reboot changes to 1')
            required_reboot = 1
            
    return required_reboot


def brightness_settings(mode):
    logger.info('\n{}[BRIGTNESS SETTINGS]{}'.format(Colors.GREEN, Colors.ENDC))
    set_brightness = ''

    if mode in MAPPING_MODES:
        brightness_setting_check = MAPPING_MODES[mode]['brightness_setting_check']
        brightness_setting_value = MAPPING_MODES[mode]['brightness_setting_value']
        if config.getboolean('SETTINGS', brightness_setting_check):
            set_brightness = config.get('SETTINGS', brightness_setting_value)

    if config.getboolean('CONFIGURATION', 'application_on'):

        if set_brightness != '':

            if os.path.isdir("/sys/class/backlight"):
                logger.debug('/sys/class/backlight exists.')
                for name in os.listdir("/sys/class/backlight"):

                    if os.path.isfile("/sys/class/backlight/" + name + "/max_brightness") and os.path.isfile(
                            "/sys/class/backlight/" + name + "/brightness"):
                        brilloMax = int(subprocess.getoutput("cat /sys/class/backlight/" + name + "/max_brightness"))
                        brightness = int((brilloMax / 100) * int(set_brightness))

                        exit_code = subprocess.getstatusoutput(
                            'echo {} > /sys/class/backlight/{}/brightness'.format(brightness, name)
                        )[0]
                        logger.info('Setting Brightness (mode {})  to {} <--> {} % ... | Exit: {}'.format(
                            mode, brightness, set_brightness, exit_code
                        ))

                        # CRONTAB EDIT
                        if not os.path.isfile("/var/spool/cron/crontabs/root"):
                            os.system('''cp /usr/share/slimbookbattery/src/root /var/spool/cron/crontabs/root
                                        chmod 600 /var/spool/cron/crontabs/root')
                                        chgrp crontab /var/spool/cron/crontabs/root''')
                        if subprocess.getstatusoutput(
                                'cat /var/spool/cron/crontabs/root | grep slimbookbattery'
                        )[0] == 0:
                            subprocess.getoutput(
                                'sed -i "/slimbookbattery/ c@reboot /usr/bin/slimbookbattery-pkexec autostart" '
                                '/var/spool/cron/crontabs/root')
                            logger.debug('Crontab settings added')
                        else:
                            subprocess.getoutput(
                                "sed -i '$a @reboot /usr/bin/slimbookbattery-pkexec autostart' "
                                "/var/spool/cron/crontabs/root")
                            logger.debug('Crontab settings added')
                    else:
                        logger.error('Brightness file not found')

            else:
                logger.error('Brightness directory not found')
        else:
            # CRONTAB EDIT
            logger.info('Brightness setting is off')
            if not os.path.isfile("/var/spool/cron/crontabs/root"):
                os.system('''cp /usr/share/slimbookbattery/src/root /var/spool/cron/crontabs/root
                            chmod 600 /var/spool/cron/crontabs/root')
                            chgrp crontab /var/spool/cron/crontabs/root''')
            if os.system('cat /var/spool/cron/crontabs/root | grep slimbookbattery') == 0:
                os.system(
                    'sed -i "/slimbookbattery/ c#@reboot /usr/bin/slimbookbattery-pkexec autostart" '
                    '/var/spool/cron/crontabs/root')
                logger.debug('Crontab settings commented')

    else:  # Disabling crontab settings
        logger.info('Application is off --> Restoring brightnes management')
        if not os.path.isfile("/var/spool/cron/crontabs/root"):
            os.system('''cp /usr/share/slimbookbattery/src/root /var/spool/cron/crontabs/root
                        chmod 600 /var/spool/cron/crontabs/root')
                        chgrp crontab /var/spool/cron/crontabs/root''')
        if os.system('cat /var/spool/cron/crontabs/root | grep slimbookbattery') == 0:
            os.system(
                'sed -i "/slimbookbattery/ c#@reboot /usr/bin/slimbookbattery-pkexec autostart" '
                '/var/spool/cron/crontabs/root')
            logger.debug('Crontab settings commented')


def update_config(filepath, variable, value):
    print(variable, value)
    try:
        call = subprocess.getoutput('cat ' + filepath)
        patron = re.compile(r'{}=(.*)'.format(variable))
        last_value = patron.search(call)[1]
    except Exception:
        last_value = ''

    print(last_value, filepath)

    if last_value != value:
        command = "sudo sed -i '/" + variable + "/ c" + variable + "=" + value + "' " + filepath
        if os.system(command) == 0:
            logger.info("Info: {} updated in {}, value: {}".format(variable, filepath, value))
        else:
            logger.error('Sed command failed')
            return 1
    else:
        logger.info('Already set in {}'.format(filepath))

    return 0


if __name__ == "__main__":
    main(sys.argv)
