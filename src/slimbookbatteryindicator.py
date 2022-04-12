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

import configparser
import logging
import os
import signal
import subprocess
import sys
from datetime import date
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, GdkPixbuf

try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator3
except:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as AppIndicator3
# We want load first current location
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
if CURRENT_PATH not in sys.path:
    sys.path = [CURRENT_PATH] + sys.path
import utils, tdp_utils

srcpath = '/usr/share/slimbookbattery/src'
sys.path.insert(1, srcpath)

_ = utils.load_translation('slimbookbattery')

USER_NAME = utils.get_user()
HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))

CONFIG_FILE = os.path.join(HOMEDIR,'.config','slimbookbattery','slimbookbattery.conf')
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

ICONS= {
    "1": "normal",
    "2": "balanced_normal",
    "3": "performance_normal",
    "0": "disabled_normal",
}

APP_INDICATOR_ID = 'Slimbook Battery Indicator'

ICONS_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '..', 'images', 'indicator'))
                                        
logger = logging.getLogger()   

class Indicator(Gtk.Application):
    
    current_mode = config.get('CONFIGURATION', 'modo_actual')
    
    def __init__(self):
        
        self.app = 'show_proc'

        self.indicator = AppIndicator3.Indicator.new('show_proc', ICONS_PATH+"/normal.png", AppIndicator3.IndicatorCategory.OTHER)
        			                                 
        self.indicator.set_icon_theme_path(os.path.join(CURRENT_PATH, '..', 'images', 'indicator'))

        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.indicator.set_title('Slimbook Battery')

        self.indicator.set_menu(self.get_menu())
        
        if config.getboolean('CONFIGURATION', 'plug_warn'):
            check_plug()

        if config.getboolean('CONFIGURATION', 'icono'):
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        else:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

        if config.getboolean('CONFIGURATION', 'application_on'):

            if os.system("pkexec slimbookbattery-pkexec autostart") == 0:
                logger.debug('Brightness set')

            mode = config.getint('CONFIGURATION', 'modo_actual')
            self.indicator.set_icon_full(ICONS.get(str(mode)), 'Mode')
        else:
            self.indicator.set_icon_full(ICONS.get(str('0')), 'Icon disabled')

    def get_menu(self):
        menu = Gtk.Menu()
        ITEMS = [
        {
            'label_name': _('Energy Saving'),    
            'pixbuf': 'normal.png',
            'function': self.modo_ahorro
        },
        {
            'label_name': _('Balanced'),
            'pixbuf': 'balanced_normal.png',
            'function': self.modo_equilibrado
        },
        {
            'label_name': _('Maximum Performance'),
            'pixbuf': 'performance_normal.png',
            'function': self.modo_max_rendimiento
        },
        {
            'label_name': _('Off'),
            'pixbuf': 'disabled_normal.png',
            'function': self.modo_apagado
        },
        {
            'label_name': _('Advanced mode'),
            'function': self.modo_avanzado
        },
        {
            'label_name': _('Exit'),
            'function': self.salir
        }]
        
        for line, data in enumerate(ITEMS, start=1):
            # Se añaden los items al menú en orden
            if line > 3:
                separator = Gtk.SeparatorMenuItem()
                menu.append(separator) 
                
            if 'pixbuf' in data:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename=os.path.join(ICONS_PATH, data.get('pixbuf')),
                    width=25,
                    height=25,
                    preserve_aspect_ratio=True)
                
                icon = Gtk.Image.new_from_pixbuf(pixbuf)
                item = Gtk.ImageMenuItem(label=_('Medium performance'), image=icon)     
                item.set_always_show_image(True)
                
            else:
                item = Gtk.MenuItem()
                
            item.set_label(data.get('label_name'))
            item.connect('activate', data.get('function'))  
            menu.append(item)
        
        menu.show_all()

        return menu

    def update_mode(self):
        
        if self.current_mode != '0':
            update_config('CONFIGURATION', 'application_on', '1')
            update_config('CONFIGURATION', 'modo_actual', self.current_mode)
        else:
            update_config('CONFIGURATION', 'application_on', '0')
            
        subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))
        icon = ICONS.get(str(self.current_mode))
        self.indicator.set_icon_full(icon, 'Mode')

        if config.getboolean('TDP', 'saving_tdpsync'):    
            tdp_utils.set_mode(self.current_mode)
            exit, msg = tdp_utils.reboot_indicator()
            if exit != 0: logger.error(msg)         
        
        animations(self.current_mode)

    def modo_ahorro(self, item):
        self.current_mode = '1'
        self.update_mode()
        logger.debug('Energy Saving Mode')

    def modo_equilibrado(self, item):
        self.current_mode = '2'
        self.update_mode()
        logger.debug('Balanced Power Mode')

    def modo_max_rendimiento(self, item):
        self.current_mode = '3'
        self.update_mode()
        logger.debug('Full Power Mode')

    def modo_avanzado(self, item):
        logger.debug('preferencias')
        os.system(os.path.join(CURRENT_PATH, 'slimbookbatterypreferences.py'))

    def modo_apagado(self, item):
        self.current_mode = '0'
        update_config('CONFIGURATION', 'application_on', '0')
        self.update_mode()
        logger.debug('Off')

    def salir(self, item):
        os.system('pkexec slimbookbattery-pkexec service stop')
        Gtk.main_quit()

def check_plug():
    last = config.get('CONFIGURATION', 'plugged')
    if not last == '':
        last = last.split('-')
        last_date = []
        for value in last:
            last_date.append(int(value))

        last_date = date(last_date[0], last_date[1], last_date[2])

        today = date.today()

        last_plug = abs(last_date - today).days

        if last_plug >= 15:
            code, stdout = subprocess.getstatusoutput("cat /sys/class/power_supply/BAT0/status")

            if code == 0 and stdout != 'Discharging':
                cmd = 'notify-send --icon {} "Slimbook Battery" "{}"'.format(
                    os.path.join(CURRENT_PATH, '../images/normal.png'),
                    _('It seems that you have been connected to AC for at least 15 days, '
                      'we recommend you to disconnect your charger, and discharge battery')
                )
                os.system(cmd)
            else:
                logger.debug('Resetting last unplugged date')
                config.set('CONFIGURATION', 'plugged', str(date.today()))
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)

        logger.info('Time since last time disconnection: {} days'.format(last_plug))
    else:
        logger.debug('No date saved')

        config.set('CONFIGURATION', 'plugged', str(date.today()))
        # This step is done at the end of function
        with open(os.path.join(HOMEDIR, '.config/slimbookbattery/slimbookbattery.conf'), 'w') as configfile:
            config.write(configfile)

def animations(mode):
    exitcode, stdout = subprocess.getstatusoutput('echo $XDG_CURRENT_DESKTOP | grep -i gnome')

    if exitcode == 0:
        logger.info('Setting mode {} animations'.format(mode))
        
        MODES = {
            "0": True,
            "1": config.getboolean('SETTINGS', 'ahorro_animations'),
            "2": config.getboolean('SETTINGS', 'equilibrado_animations'),
            "3": config.getboolean('SETTINGS', 'equilibrado_animations')
        }
        try:
            animations = MODES.get(str(mode))
        except:
            logger.error('Mode not found')
            animations = True
        
        if animations:
            logger.debug('Animations Active')
            os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')
        else:
            logger.debug('Animations Inactive')
            os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
            
       
    else:
        logger.error('Not Gnome desktop {} {}'.format(exitcode, stdout))

def update_config(section, variable, value):
    # We change our variable: config.set(section, variable, value)
    config.set(section, variable, str(value))

    # Writing our configuration file
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    logger.info("- Variable |{}| updated in .conf, current value: {}".format(variable, value))

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if config.getboolean('CONFIGURATION', 'alerts'):
        if not os.path.isfile('/lib/systemd/system/slimbookbattery.service'):
            logger.info('Creating notification service')
            os.system('pkexec slimbookbattery-pkexec service create')

        logger.debug('Opening notification service')
        os.system('pkexec slimbookbattery-pkexec service restart')

    Indicator()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
