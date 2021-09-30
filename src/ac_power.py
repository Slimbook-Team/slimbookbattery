#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import locale
import gettext
import subprocess
import configparser 
from time import sleep
from datetime import date

USERNAME = subprocess.getstatusoutput("logname")

if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd ' + USERNAME[1]) == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))

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

current_path = os.path.dirname(os.path.realpath(__file__))

t = gettext.translation('preferences',
                        current_path + '/locale',
                        languages=idiomas,
                        fallback=True)
_ = t.gettext

config_file = HOMEDIR + '/.config/slimbookbattery/slimbookbattery.conf'

config = configparser.ConfigParser()
config.read(config_file)



cmd = (subprocess.getstatusoutput("cat /sys/class/power_supply/BAT0/status"))

if cmd[0] == 0:
    status = cmd[1]

    if status == 'Discharging':
        config.set('CONFIGURATION', 'plugged', str(date.today()))
        configfile = open(config_file, 'w')
        config.write(configfile)
        configfile.close()

else:
    status = (_('Unknown'))

print(status)



