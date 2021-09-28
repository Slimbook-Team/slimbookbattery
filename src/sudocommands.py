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
import gettext
import os
import re
import subprocess
import sys
from configparser import ConfigParser

import locale

print('******************************************************************************')

print('\x1b[6;30;42m' + 'SlimbookBattery-Commandline, executed as: ' + str(subprocess.getoutput('whoami')) + '\x1b[0m')

USERNAME = subprocess.getstatusoutput("logname")

if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd ' + USERNAME[1]) == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

#subprocess.getstatusoutput('echo $(date) ' + USER_NAME + '>> /var/slimbookbattery.log')

HOMEDIR = subprocess.getoutput("echo ~" + USER_NAME)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
currpath = os.path.dirname(os.path.realpath(__file__))

print("Username: " + str(USER_NAME) + " - Homedir: " + HOMEDIR + "")

config_file = HOMEDIR + '/.config/slimbookbattery/slimbookbattery.conf'
config = ConfigParser()
config.read(config_file)

tdpcontroller = config['TDP']['tdpcontroller']
tdp_config_file = HOMEDIR + '/.config/' + tdpcontroller + '/' + tdpcontroller + '.conf'

config_tdp = ConfigParser()
config_tdp.read(tdp_config_file)

idiomas = ['en']
try:
    entorno_usu = locale.getlocale()[0]
    for lang in ["en", "es", "it", "pt", "gl"]:
        if entorno_usu.find(lang) >= 0:
            idiomas = [entorno_usu]
            break
    print('Language: ', entorno_usu)
except Exception:
    print('Locale exception')

t = gettext.translation('sudocommands',
                        currpath + '/locale',
                        languages=idiomas,
                        fallback=True)
_ = t.gettext

msg_graphics = _('Graphics settings have been modified, changes will be applied on restart.')


class colors:  # You may need to change color settings
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    CYAN = "\033[1;36m"
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    BOLD = "\033[;1m"

def main(args):  # Args will be like --> command_name value

    arguments = ''
    for argument in range(len(args)):
        if argument != 0:
            arguments = arguments + ' ' + (args[argument])
    print("Arguments: " + arguments + "\n")

    if (len(args)) > 1:
        battery_mode = config.get('CONFIGURATION', 'modo_actual')

        if args[1] == "apply":  # Applies selected mode conf and turns on/off tlp
            mode_name = ''
            # Copies selected custom mode conf to /etc/tlp.conf
            # print('Passing Custom Configuration '+battery_mode+' to tlp.conf')

            if battery_mode == '1':
                print('Power saving mode')
                mode_name = 'ahorrodeenergia'

            elif battery_mode == '2':
                print('Normal power mode')
                mode_name = 'equilibrado'

            elif battery_mode == '3':
                print('Full power mode')
                mode_name = 'maximorendimiento'

            brightness_settings(battery_mode)  # Executed by indicator
            set_tdp(battery_mode)

            # print('\n[COPY TDP CUSTOM SETTINGS]')
            print(colors.GREEN + "\n[COPY TDP CUSTOM SETTINGS]" + colors.ENDC)
            exec = subprocess.getstatusoutput(
                "sudo cp " + HOMEDIR + "/.config/slimbookbattery/custom/" + mode_name + " /etc/tlp.conf")
            if exec[0] == 0:
                print('File copied succesfully!')
            else:
                print('Execution failed ' + exec[1])

            if config.get('CONFIGURATION',
                          'application_on') == '1':  # Sets mode changes and enables/disables TLP according to conf
                # Extra configuration
                if update_config('/etc/tlp.conf', 'TLP_ENABLE', '1') == 0:
                    print('TLP is enabled')

            else:  # Disablig TLP in conf
                if update_config('/etc/tlp.conf', 'TLP_ENABLE', '0') == 0:
                    print('TLP is disabled')

            # Restarting TLP
            subprocess.getoutput("sudo tlp start")

            required_reboot = mode_settings(battery_mode)
            if required_reboot == 1:
                print('Sudo notify')
                notify(msg_graphics)

            # print(str(os.system(command)))

            exit(required_reboot)

        if args[1] == "restore":

            # Copies selected DEFAULT conf to CUSTOM conf (also slimbookbattery.conf)
            home_file = os.path.join(HOMEDIR, ".config/slimbookbattery/slimbookbattery.conf")
            print(str(subprocess.getstatusoutput(
                "sudo cp /usr/share/slimbookbattery/src/slimbookbattery.conf " + home_file)[0]))
            home_file = os.path.join(HOMEDIR, ".config/slimbookbattery/ahorrodeenergia")
            print(str(subprocess.getstatusoutput(
                "sudo cp " + HOMEDIR + "/.config/slimbookbattery/default/ahorrodeenergia " + home_file)[0]))
            home_file = os.path.join(HOMEDIR, ".config/slimbookbattery/equilibrado")
            print(str(subprocess.getstatusoutput(
                "sudo cp " + HOMEDIR + "/.config/slimbookbattery/default/equilibrado " + home_file)[0]))
            home_file = os.path.join(HOMEDIR, ".config/slimbookbattery/maximorendimiento")
            print(str(subprocess.getstatusoutput(
                "sudo cp " + HOMEDIR + "/.config/slimbookbattery/default/maximorendimiento " + home_file)[0]))

            #
            if battery_mode == '1':
                print('Power saving mode selected')
                subprocess.getstatusoutput(
                    "sudo cp " + HOMEDIR + "/.config/slimbookbattery/custom/ahorrodeenergia /etc/tlp.conf")

            elif battery_mode == '2':
                print('Normal power mode selected')
                os.system("sudo cp " + HOMEDIR + "/.config/slimbookbattery/custom/equilibrado /etc/tlp.conf")

            elif battery_mode == '3':
                print('Full power mode selected')
                os.system("sudo cp " + HOMEDIR + "/.config/slimbookbattery/custom/maximorendimiento /etc/tlp.conf")

        if args[1] == "autostart":  # Sets brightness and enables tdp
            battery_mode = config.get('CONFIGURATION', 'modo_actual')
            brightness_settings(battery_mode)

        if args[1] == "report":
            os.system(
                "sudo python3 " + currpath + "/slimbookbattery-report.py " + args[2] + ' ' + args[3] + ' ' + args[4])

        if args[1] == "restart_tlp":
            print('Restarting TLP...')
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

    print('******************************************************************************\n')


def notify(msg):
    os.system('''set -x
                display=":$(ls /tmp/.X11-unix/* | sed 's#/tmp/.X11-unix/X##' | head -n 1)"
                user=''' + USER_NAME + '''
                uid=$(id -u $user)
                sudo -u $user DISPLAY=$display DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$uid/bus notify-send "Slimbook Battery" "''' + msg + '''"
                ''')


def set_tdp(mode):
    # This function enables tdpcontroller autostart an changes it's mode if battery application,
    # battery autostart and sync tdp switch of the selected mode is on.
    print(colors.GREEN + '\n[TDP SETTINGS]' + colors.ENDC)
    print('Battery Mode: ' + mode)

    # Mode settings
    if config['CONFIGURATION']['application_on'] == '1':

        tdp_switch = ''
        tdp_mode = ''
        tdp_switch = 'saving_tdpsync'

        if mode == '1':           
            tdp_mode = 'low'

        elif mode == '2':            
            tdp_mode = 'medium'

        elif mode == '3':           
            tdp_mode = 'high'


        try:
            if config['TDP'][tdp_switch] == '1':
                print('Updating TDP mode ...')
                config_tdp.set('CONFIGURATION', 'mode', tdp_mode)
                print('  TDP changed to ' + config_tdp['CONFIGURATION']['mode'])

                # Autostart settings
                print('\nUpdating TDP autostart ...')
                if config['CONFIGURATION']['autostart'] == '1':
                    config_tdp.set('CONFIGURATION', 'autostart', 'on')
                    print('  TDP Autostart enabled')
                    if config_tdp['CONFIGURATION']['show-icon'] == 'on':
                        print('  TDP Icon will be shown')
                    else:
                        config_tdp.set('CONFIGURATION', 'show-icon', 'off')

                configfile = open(tdp_config_file, 'w')
                config_tdp.write(configfile)
                configfile.close()

                print('Actual TDP Mode: ' + config_tdp['CONFIGURATION']['mode'])

            else:
                print('TDP Sync not active')

        except Exception:
            print('Could not sync TDP')

    else:
        print('Not changing ' + tdpcontroller + ' mode configuration.')


def change_config(args):  # For general page options
    print(colors.GREEN + '\n[CHANGE CONFIGURATION]' + colors.ENDC)
    files = ['/etc/tlp.conf',
             HOMEDIR + '/.config/slimbookbattery/custom/ahorrodeenergia',
             HOMEDIR + '/.config/slimbookbattery/custom/equilibrado',
             HOMEDIR + '/.config/slimbookbattery/custom/maximorendimiento']

    for file in files:
        update_config(file, args[2], args[3])


def mode_settings(mode):
    required_reboot = 0
    print(colors.GREEN + '\n[MODE SETTINGS]' + colors.ENDC)
    file_ahorro = HOMEDIR + '/.config/slimbookbattery/custom/ahorrodeenergia'
    file_equilibrado = HOMEDIR + '/.config/slimbookbattery/custom/equilibrado'
    file_max = HOMEDIR + '/.config/slimbookbattery/custom/maximorendimiento'

    graficaNvidia = False
    graphics_before = ''

    # Checking graphics
    stout = subprocess.getoutput('prime-select query')
    nvidia = subprocess.getstatusoutput("prime-select " + stout + "| grep -i 'profile is already set'")
    if nvidia[0] == 0:  #
        graficaNvidia = True
        graphics_before = stout

    # If nvidia driver is installed and works WE SET IT MANUALLY
    if graficaNvidia:
        print('Detected nvidia graphics profile: ' + graphics_before)
        print('Setting new profile ...')
        if mode == '1':

            if config['SETTINGS']['graphics_ahorro'] == '1' and graphics_before != 'intel':
                if not graphics_before == 'intel':
                    os.system('prime-select intel')

            elif config['SETTINGS']['graphics_ahorro'] == '0' and graphics_before != 'on-demand':
                if not graphics_before == 'on-demand':
                    os.system('prime-select intel')
                    # avocado
                    os.system('prime-select on-demand')

        elif mode == '2':

            if config['SETTINGS']['graphics_equilibrado'] == '1' and graphics_before != 'on-demand':
                if not graphics_before == 'on-demand':
                    os.system('prime-select intel')
                    os.system('prime-select on-demand')

            elif config['SETTINGS']['graphics_equilibrado'] == '0' and graphics_before != 'nvidia':
                if not graphics_before == 'nvidia':
                    os.system('prime-select nvidia')

        elif mode == '3': #need to check
            if config['SETTINGS']['graphics_maxrendimiento'] == '1' and graphics_before != 'on-demand':
                if not graphics_before == 'on-demand':
                    os.system('prime-select intel')
                    os.system('prime-select on-demand')

            elif config['SETTINGS']['graphics_maxrendimiento'] == '0' and graphics_before != 'nvidia':
                if not graphics_before == 'nvidia':
                    os.system('prime-select nvidia')

        graphics_after = subprocess.getoutput('prime-select query')
        print('Graphics before --> ' + graphics_before + ' // Graphics after --> ' + graphics_after)
        if not graphics_before == graphics_after:
            print('Required reboot changes to 1')
            required_reboot = 1

    # If nvidia driver is not installed or does not work, we use TLP
    elif not graficaNvidia:
        print('Setting graphics frequency ...')
        # GRAPHICS AMD SETTINGS de
        RADEON_POWER_PROFILE_ON_BAT = 'default'
        RADEON_DPM_STATE_ON_BAT = 'battery'
        RADEON_DPM_PERF_LEVEL_ON_BAT = 'auto'

        # GRAPHICS INTEL SETTINGS
        freq_table = ''
        freq_available = ''

        if os.path.isfile('/sys/kernel/debug/dri/0/i915_ring_freq_table'):
            freq_table = subprocess.getoutput('cat /sys/kernel/debug/dri/0/i915_ring_freq_table')
            freq_table = freq_table.split('\n')
            freq_table.pop(0)
            freq_available = ''

            for i in freq_table:
                valor = i.split()
                freq_available = freq_available + ' ' + valor[0]

            freq_available = freq_available.strip().split(' ')

            # FRECUENCIAS PARA LOS MODOS
            if len(freq_available) > 1:
                freqCorrecta = True
                min_bat = 0
                min_ac = 0
                max_bat = 0
                max_ac = 0
                boost_bat = 0
                boost_ac = 0

        if mode == '1':

            # if config['SETTINGS']['graphics_ahorro'] == '1' and os.system('lscpu | grep model | grep Radeon'):
            if config['SETTINGS']['graphics_ahorro'] == '1':
                # Radeon 
                if subprocess.getstatusoutput('lscpu | grep -i model | grep  -i Radeon')[0] == 0:
                    print('Radeon graphics power profile: low')
                    RADEON_POWER_PROFILE_ON_BAT = 'low'
                    os.system(
                        'sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ cRADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                            RADEON_POWER_PROFILE_ON_BAT, file_equilibrado
                        )
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_STATE_ON_BAT=/ cRADEON_DPM_STATE_ON_BAT={}" {}'.format(
                            RADEON_DPM_STATE_ON_BAT, file_equilibrado
                        )
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ cRADEON_DPM_PERF_LEVEL_ON_BAT={}" {}'.format(
                            RADEON_DPM_PERF_LEVEL_ON_BAT, file_ahorro
                        )
                    )

                # Intel 
                elif subprocess.getstatusoutput('lspci | grep VGA | grep -i Intel')[0] == 0:
                    print('Intel graphics power profile: low')
                    # MIN_BAT/MIN_AC
                    # Si el valor que queremos se encuentra dentro del array se usará ese,
                    # sino se buscara dentro del array dentro del rango que se indica
                    for i in range(len(freq_available)):
                        if (int(freq_available[i]) > 0 and int(freq_available[i]) < 600):
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
                            if (int(freq_available[i]) >= 600 and int(freq_available[i]) < 800):
                                max_bat = int(freq_available[i])
                                break
                        if max_bat == 0:
                            freqCorrecta = False

                        if int(freq_available[-1]) > 0 and freqCorrecta:
                            max_ac = int(freq_available[-1])
                        if max_ac == 0:
                            freqCorrecta = False

                        # BOOST_BAT/BOOST_AC
                        if freqCorrecta:
                            for i in range(len(freq_available)):
                                if (int(freq_available[i]) >= 800 and int(freq_available[i]) < int(freq_available[-1])):
                                    boost_bat = int(freq_available[i])
                                    break
                            if boost_bat == 0:
                                freqCorrecta = False

                            if int(freq_available[-1]) > 0 and freqCorrecta:
                                boost_ac = int(freq_available[-1])
                            if boost_ac == 0:
                                freqCorrecta = False

                    # Si el boolean sigue en True querrá decir que se han obtenido valores para min, max y boost y
                    # se llamará al script para poder realizar las modificaciones
                    if freqCorrecta:
                        print('Setting GPU freq --> ' + str(min_bat), str(max_bat), str(boost_bat))
                        update_config(file_ahorro, 'INTEL_GPU_MIN_FREQ_ON_BAT', str(min_bat))
                        update_config(file_ahorro, 'INTEL_GPU_MIN_FREQ_ON_AC', str(min_ac))
                        update_config(file_ahorro, 'INTEL_GPU_MAX_FREQ_ON_BAT', str(max_bat))
                        update_config(file_ahorro, 'INTEL_GPU_MAX_FREQ_ON_AC', str(max_ac))
                        update_config(file_ahorro, 'INTEL_GPU_BOOST_FREQ_ON_BAT', str(boost_bat))
                        update_config(file_ahorro, 'INTEL_GPU_BOOST_FREQ_ON_AC', str(boost_ac))
                    else:
                        print('Frequency not changed')
                else:
                    print('Graphics 404')
            else:
                # Radeon 
                if subprocess.getstatusoutput('lscpu | grep -i model | grep -i Radeon')[0] == 0:
                    print('Radeon graphics power profile: default')
                    RADEON_POWER_PROFILE_ON_BAT = 'default'
                    os.system(
                        'sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ c#RADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                            RADEON_POWER_PROFILE_ON_BAT, file_ahorro
                        )
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_STATE_ON_BAT=/ c#RADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                            RADEON_POWER_PROFILE_ON_BAT, file_ahorro
                        )
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ c#RADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                            RADEON_DPM_PERF_LEVEL_ON_BAT, file_ahorro
                        )
                    )

                # Intel 
                elif subprocess.getstatusoutput('lspci | grep VGA | grep Intel')[0] == 0:
                    print('Intel graphics power profile: #low')
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_BAT=/ c#INTEL_GPU_MIN_FREQ_ON_BAT=0" ' + file_ahorro)
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_AC=/ c#INTEL_GPU_MIN_FREQ_ON_AC=0" ' + file_ahorro)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_BAT=/ c#INTEL_GPU_MAX_FREQ_ON_BAT=0" ' + file_ahorro)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_AC=/ c#INTEL_GPU_MAX_FREQ_ON_AC=0" ' + file_ahorro)
                    os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_BAT=/ c#INTEL_GPU_BOOST_FREQ_ON_BAT=0" ' + file_ahorro)
                    os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_AC=/ c#INTEL_GPU_BOOST_FREQ_ON_AC=0" ' + file_ahorro)
                else:
                    print('Graphics 404')

        if mode == '2':

            if config['SETTINGS']['graphics_equilibrado'] == '1':
                # Radeon integrated
                if subprocess.getstatusoutput('lscpu | grep -i model | grep  -i Radeon')[0] == 0:
                    print('Radeon graphics power profile: mid')
                    RADEON_POWER_PROFILE_ON_BAT = 'mid'
                    # Radeon changes
                    os.system(
                        'sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ cRADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                            RADEON_POWER_PROFILE_ON_BAT, file_equilibrado
                        )
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_STATE_ON_BAT=/ cRADEON_DPM_STATE_ON_BAT={}" {}'.format(
                            RADEON_DPM_STATE_ON_BAT, file_equilibrado
                        )
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ cRADEON_DPM_PERF_LEVEL_ON_BAT={}" {}'.format(
                            RADEON_DPM_PERF_LEVEL_ON_BAT, file_ahorro
                        )
                    )

                # Intel 
                elif subprocess.getstatusoutput('lspci | grep VGA | grep -i Intel')[0] == 0:
                    print('Intel graphics power profile: mid')
                    for i in range(len(freq_available)):
                        if (int(freq_available[i]) > 0 and int(freq_available[i]) < 600):
                            min_bat = int(freq_available[i])
                            # print('min_bat = '+str(min_bat))
                            min_ac = int(freq_available[i])
                            break
                    # Si el valor que se busca no se encuentra, el boolean freqCorrecta pasará a False y
                    # por lo tanto no se realizará ninguna modificación respecto a gráficas Intel
                    if min_bat == 0:
                        freqCorrecta = False
                    if min_ac == 0:
                        freqCorrecta = False

                    if freqCorrecta:
                        for i in range(len(freq_available)):
                            if (int(freq_available[i]) >= 900 and int(freq_available[i]) < 1000):
                                max_bat = int(freq_available[i])
                                # print('max_bat = '+str(max_bat))
                                break
                    if max_bat == 0:
                        freqCorrecta = False

                    if int(freq_available[-1]) > 0 and freqCorrecta:
                        max_ac = int(freq_available[-1])
                    if max_ac == 0:
                        freqCorrecta = False

                    if '1000' in freq_available and freqCorrecta:
                        boost_bat = 1000

                    if freqCorrecta:
                        for i in range(len(freq_available)):
                            if (int(freq_available[i]) >= 1000 and int(freq_available[i]) < int(freq_available[-1])):
                                boost_bat = int(freq_available[i])
                                # print('boost_bat = '+str(boost_bat))
                                break
                        if boost_bat == 0:
                            freqCorrecta = False

                    if int(freq_available[-1]) > 0 and freqCorrecta:
                        boost_ac = int(freq_available[-1])
                    if boost_ac == 0:
                        freqCorrecta = False

                    # Si el boolean sigue en True querrá decir que se han obtenido valores para min, max y boost y
                    # se llamará al script para poder realizar las modificaciones
                    if freqCorrecta:
                        print('Setting GPU freq --> ' + str(min_bat), str(max_bat), str(boost_bat))
                        update_config(file_equilibrado, 'INTEL_GPU_MIN_FREQ_ON_BAT', str(min_bat))
                        update_config(file_equilibrado, 'INTEL_GPU_MIN_FREQ_ON_AC', str(min_ac))
                        update_config(file_equilibrado, 'INTEL_GPU_MAX_FREQ_ON_BAT', str(max_bat))
                        update_config(file_equilibrado, 'INTEL_GPU_MAX_FREQ_ON_AC', str(max_ac))
                        update_config(file_equilibrado, 'INTEL_GPU_BOOST_FREQ_ON_BAT', str(boost_bat))
                        update_config(file_equilibrado, 'INTEL_GPU_BOOST_FREQ_ON_AC', str(boost_ac))
                    else:
                        print('Freq not found')
            else:
                # Radeon 
                if subprocess.getstatusoutput('lscpu | grep -i model | grep -i Radeon')[0] == 0:
                    print('Radeon graphics power profile: #default')
                    RADEON_POWER_PROFILE_ON_BAT = 'default'
                    os.system(
                        'sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ c#RADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                            RADEON_POWER_PROFILE_ON_BAT, file_equilibrado)
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_STATE_ON_BAT=/ c#RADEON_DPM_STATE_ON_BAT=0{}" {}'.format(
                            RADEON_DPM_STATE_ON_BAT, file_equilibrado
                        )
                    )
                    os.system(
                        'sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ c#RADEON_DPM_PERF_LEVEL_ON_BAT={}" {}'.format(
                            RADEON_DPM_PERF_LEVEL_ON_BAT, file_ahorro
                        )
                    )

                # Intel integrated
                elif subprocess.getstatusoutput('lspci | grep VGA | grep Intel')[0] == 0:
                    print('Intel graphics power profile: #mid')
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_BAT=/ c#INTEL_GPU_MIN_FREQ_ON_BAT=0" ' + file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_AC=/ c#INTEL_GPU_MIN_FREQ_ON_AC=0" ' + file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_BAT=/ c#INTEL_GPU_MAX_FREQ_ON_BAT=0" ' + file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_AC=/ c#INTEL_GPU_MAX_FREQ_ON_AC=0" ' + file_equilibrado)
                    os.system(
                        'sed -i "/INTEL_GPU_BOOST_FREQ_ON_BAT=/ c#INTEL_GPU_BOOST_FREQ_ON_BAT=0" ' + file_equilibrado)
                    os.system(
                        'sed -i "/INTEL_GPU_BOOST_FREQ_ON_AC=/ c#INTEL_GPU_BOOST_FREQ_ON_AC=0" ' + file_equilibrado)

        if mode == '3':
            # Radeon 
            if subprocess.getstatusoutput('lscpu | grep -i model | grep -i Radeon')[0] == 0:
                print('Radeon graphics power profile: high')
                RADEON_POWER_PROFILE_ON_BAT = 'high'
                # Radeon changes
                os.system(
                    'sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ cRADEON_POWER_PROFILE_ON_BAT={}" {}'.format(
                        RADEON_POWER_PROFILE_ON_BAT, file_equilibrado
                    )
                )
                os.system(
                    'sed -i "/RADEON_DPM_STATE_ON_BAT=/ cRADEON_DPM_STATE_ON_BAT={}" {}'.format(
                        RADEON_DPM_STATE_ON_BAT, file_equilibrado
                    )
                )
                os.system(
                    'sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ cRADEON_DPM_PERF_LEVEL_ON_BAT={}" {}'.format(
                        RADEON_DPM_PERF_LEVEL_ON_BAT, file_ahorro
                    )
                )

            # Intel integrated
            elif subprocess.getstatusoutput('lspci | grep VGA | grep Intel') == 0:
                print('Intel graphics power profile: high')
                for i in range(len(freq_available)):
                    if (int(freq_available[i]) > 0 and int(freq_available[i]) < 600):
                        min_bat = int(freq_available[i])
                        min_ac = int(freq_available[i])
                        break
                # Si el valor que se busca no se encuentra, el boolean freqCorrecta pasará a False y
                # por lo tanto no se realizará ninguna modificación respecto a gráficas Intel
                if min_bat == 0:
                    freqCorrecta = False
                if min_ac == 0:
                    freqCorrecta = False

                if int(freq_available[-1]) > 0 and freqCorrecta:
                    max_ac = int(freq_available[-1])
                    max_bat = int(freq_available[-1])
                if max_ac == 0:
                    freqCorrecta = False
                if max_bat == 0:
                    freqCorrecta = False

                if int(freq_available[-1]) > 0 and freqCorrecta:
                    boost_ac = int(freq_available[-1])
                    boost_bat = int(freq_available[-1])
                if boost_ac == 0:
                    freqCorrecta = False
                if boost_bat == 0:
                    freqCorrecta = False

                # Si el boolean sigue en True querrá decir que se han obtenido valores para
                # min, max y boost y se llamará al script para poder realizar las modificaciones
                if freqCorrecta:
                    update_config(file_max, 'INTEL_GPU_MIN_FREQ_ON_BAT', str(min_bat))
                    update_config(file_max, 'INTEL_GPU_MIN_FREQ_ON_AC', str(min_ac))
                    update_config(file_max, 'INTEL_GPU_MAX_FREQ_ON_BAT', str(max_bat))
                    update_config(file_max, 'INTEL_GPU_MAX_FREQ_ON_AC', str(max_ac))
                    update_config(file_max, 'INTEL_GPU_BOOST_FREQ_ON_BAT', str(boost_bat))
                    update_config(file_max, 'INTEL_GPU_BOOST_FREQ_ON_AC', str(boost_ac))

    return required_reboot


def brightness_settings(mode):
    print(colors.GREEN + '\n[BRIGTNESS SETTINGS]' + colors.ENDC)
    set_brightness = ''

    if mode == '1':
        if config.get('SETTINGS', 'saving_brightness_switch') == '1':
            set_brightness = config.get('SETTINGS', 'ahorro_brightness')

    elif mode == '2':
        if config.get('SETTINGS', 'balanced_brightness_switch') == '1':
            set_brightness = config.get('SETTINGS', 'equilibrado_brightness')

    elif mode == '3':
        if config.get('SETTINGS', 'power_brightness_switch') == '1':
            set_brightness = config.get('SETTINGS', 'maxrendimiento_brightness')

    if config.get('CONFIGURATION', 'application_on') == '1':

        if set_brightness != '':

            if os.path.isdir("/sys/class/backlight"):
                for name in os.listdir("/sys/class/backlight"):
                    if os.path.isfile("/sys/class/backlight/" + name + "/max_brightness") and os.path.isfile(
                            "/sys/class/backlight/" + name + "/brightness"):
                        brilloMax = int(subprocess.getoutput("cat /sys/class/backlight/" + name + "/max_brightness"))
                        brightness = int((brilloMax / 100) * int(set_brightness))
                        print('Setting Brightness (mode' + mode + ')  to ' + str(
                            brightness) + ' <--> ' + set_brightness + ' % ... | Exit: ' + str(
                            subprocess.getstatusoutput(
                                'echo ' + str(brightness) + ' > /sys/class/backlight/' + name + '/brightness')[0]))

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
                            print('Crontab settings added')
                        else:
                            subprocess.getoutput(
                                "sed -i '$a @reboot /usr/bin/slimbookbattery-pkexec autostart' "
                                "/var/spool/cron/crontabs/root")
                            print('Crontab settings added')
        else:
            # CRONTAB EDIT
            print('Brightness setting is off')
            if not os.path.isfile("/var/spool/cron/crontabs/root"):
                os.system('''cp /usr/share/slimbookbattery/src/root /var/spool/cron/crontabs/root
                            chmod 600 /var/spool/cron/crontabs/root')
                            chgrp crontab /var/spool/cron/crontabs/root''')
            if os.system('cat /var/spool/cron/crontabs/root | grep slimbookbattery') == 0:
                os.system(
                    'sed -i "/slimbookbattery/ c#@reboot /usr/bin/slimbookbattery-pkexec autostart" '
                    '/var/spool/cron/crontabs/root')
                print('Crontab settings commented')

    else:  # Disabling crontab settings
        print('Application is off --> Restoring brightnes management')
        if not os.path.isfile("/var/spool/cron/crontabs/root"):
            os.system('''cp /usr/share/slimbookbattery/src/root /var/spool/cron/crontabs/root
                        chmod 600 /var/spool/cron/crontabs/root')
                        chgrp crontab /var/spool/cron/crontabs/root''')
        if os.system('cat /var/spool/cron/crontabs/root | grep slimbookbattery') == 0:
            os.system(
                'sed -i "/slimbookbattery/ c#@reboot /usr/bin/slimbookbattery-pkexec autostart" '
                '/var/spool/cron/crontabs/root')
            print('Crontab settings commented')


def update_config(file, variable, value):
    try:
        call = subprocess.getoutput('cat ' + file)
        patron = re.compile(variable + '\=(.*)')
        last_value = patron.search(call)[1]
    except Exception:
        last_value = ''
    # print(last_value, value)

    if last_value != value:
        command = "sudo sed -i '/" + variable + "/ c" + variable + "=" + value + "' " + file
        # print(command)
        if os.system(command) == 0:
            print("\nInfo: " + variable + " updated in " + file + ", value: " + value)
        else:
            print('\n Sed command failed')
            return 1
    else:
        print('Already set in ' + file)

    return 0


if __name__ == "__main__":
    # Se obtiene las variables que se le pasa desde el archivo /usr/share/slimbookface/slimbookface
    main(sys.argv)
