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

# We want load first current location
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
if CURRENT_PATH not in sys.path:
    sys.path = [CURRENT_PATH] + sys.path
import utils

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, GdkPixbuf, AppIndicator3, Notify

USER_NAME = utils.get_user()
_ = utils.load_translation('slimbookbattery')

IMAGES_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '../images'))

subprocess.getstatusoutput('echo $(date) @' + USER_NAME + '>> /tmp/slimbookbattery.user')

HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))

config_file = os.path.join(HOMEDIR, '.config/slimbookbattery/slimbookbattery.conf')
config = configparser.ConfigParser()
config.read(config_file)

ENERGY_SAVING = os.path.join(IMAGES_PATH, 'indicator/normal.png')
BALANCED = os.path.join(IMAGES_PATH, 'indicator/balanced_normal.png')
MAX_PERFORMANCE = os.path.join(IMAGES_PATH, 'indicator/performance_normal.png')

DISABLED = os.path.join(IMAGES_PATH, 'indicator/disabled_normal.png')

APP_INDICATOR_ID = 'Slimbook Battery Indicator'

IMAGES_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '..', 'images'))

logger = logging.getLogger()


class Indicator(Gtk.Application):
    current_mode = config.get('CONFIGURATION', 'modo_actual')

    def __init__(self):

        if config.getboolean('CONFIGURATION', 'plug_warn'):
            self.check_plug()

        if config.getboolean('CONFIGURATION', 'icono'):
            indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        else:
            indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

        indicator.set_menu(self.build_menu())
        Notify.init(APP_INDICATOR_ID)

        if config.getboolean('CONFIGURATION', 'application_on'):

            if os.system("pkexec slimbookbattery-pkexec autostart") == 0:
                logger.debug('Brightness set')

            current_mode = config.getint('CONFIGURATION', 'modo_actual')
            if current_mode == 1:
                indicator.set_icon_full(ENERGY_SAVING, 'Icon energy saving')
            elif current_mode == 2:
                indicator.set_icon_full(BALANCED, 'Icon balanced')
            elif current_mode == 3:
                indicator.set_icon_full(MAX_PERFORMANCE, 'Icon max performance')

        else:
            indicator.set_icon_full(DISABLED, 'Icon energy saving')

    @staticmethod
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
                    with open(config_file, 'w') as configfile:
                        config.write(configfile)

            logger.info('Time since last time disconnection: {} days'.format(last_plug))
        else:
            logger.debug('No date saved')

            config.set('CONFIGURATION', 'plugged', str(date.today()))
            # This step is done at the end of function
            with open(os.path.join(HOMEDIR, '.config/slimbookbattery/slimbookbattery.conf'), 'w') as configfile:
                config.write(configfile)

    def build_menu(self):
        menu = Gtk.Menu()

        # Creación de los separadores
        item_separador1 = Gtk.SeparatorMenuItem()
        item_separador2 = Gtk.SeparatorMenuItem()
        item_separador3 = Gtk.SeparatorMenuItem()

        # Imagenes a utilizar para los iconos del menú
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'normal.png'),
            width=25,
            height=25,
            preserve_aspect_ratio=True)
        icon_ahorro = Gtk.Image.new_from_pixbuf(pixbuf)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'balanced_normal.png'),
            width=25,
            height=25,
            preserve_aspect_ratio=True)
        icon_equilibrado = Gtk.Image.new_from_pixbuf(pixbuf)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'performance_normal.png'),
            width=25,
            height=25,
            preserve_aspect_ratio=True)
        icon_max_rendimiento = Gtk.Image.new_from_pixbuf(pixbuf)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'disabled_normal.png'),
            width=25,
            height=25,
            preserve_aspect_ratio=True)
        icon_apagado = Gtk.Image.new_from_pixbuf(pixbuf)
        icon_apagado.set_pixel_size(24)

        # Creación de cada ImageMenuItem
        item_modo1 = Gtk.ImageMenuItem()
        item_modo1.set_label(_('Energy Saving'))
        item_modo1.connect('activate', self.modo_ahorro)
        item_modo1.set_image(icon_ahorro)
        item_modo1.set_always_show_image(True)

        item_modo2 = Gtk.ImageMenuItem()
        item_modo2.set_label(_('Balanced'))
        item_modo2.connect('activate', self.modo_equilibrado)
        item_modo2.set_image(icon_equilibrado)
        item_modo2.set_always_show_image(True)

        item_modo3 = Gtk.ImageMenuItem()
        item_modo3.set_label(_('Maximum Performance'))
        item_modo3.connect('activate', self.modo_max_rendimiento)
        item_modo3.set_image(icon_max_rendimiento)
        item_modo3.set_always_show_image(True)

        item_apagar = Gtk.ImageMenuItem()
        item_apagar.set_label(_('Off'))
        item_apagar.connect('activate', self.modo_apagado)
        item_apagar.set_image(icon_apagado)
        item_apagar.set_always_show_image(True)

        item_avanzado = Gtk.MenuItem()
        item_avanzado.set_label(_('Advanced mode'))
        item_avanzado.connect('activate', self.modo_avanzado)

        item_salir = Gtk.MenuItem()
        item_salir.set_label(_('Exit'))
        item_salir.connect('activate', self.salir)

        # Se añaden los items al menú en orden
        menu.append(item_modo1)
        menu.append(item_modo2)
        menu.append(item_modo3)
        menu.append(item_separador1)
        menu.append(item_apagar)
        menu.append(item_separador2)
        menu.append(item_avanzado)
        menu.append(item_separador3)
        menu.append(item_salir)

        menu.show_all()

        return menu

    def update_update_mode(self):
        update_config('CONFIGURATION', 'application_on', '1')
        update_config('CONFIGURATION', 'modo_actual', self.current_mode)
        subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))

        tdpcontroller = config.get('TDP', 'tdpcontroller')
        controller_path = os.path.join('/usr/share/', tdpcontroller, 'src', tdpcontroller, 'indicator.py')
        reboot_process(tdpcontroller, controller_path)
        animations(self.current_mode)

    def modo_ahorro(self, item):
        indicator.set_icon_full(ENERGY_SAVING, 'Icon energy saving')
        logger.debug('Battery Saving Mode')
        self.current_mode = '1'
        self.update_update_mode()

    def modo_equilibrado(self, item):
        indicator.set_icon_full(BALANCED, 'Icon balanced')
        logger.debug('Normal power mode')
        self.current_mode = '2'
        self.update_update_mode()

    def modo_max_rendimiento(self, item):
        indicator.set_icon_full(MAX_PERFORMANCE, 'Icon max performance')
        logger.debug('Full Power Mode')
        self.current_mode = '3'
        self.update_update_mode()

    def modo_avanzado(self, item):
        logger.debug('preferencias')
        os.system(os.path.join(CURRENT_PATH, 'slimbookbatterypreferences.py'))

    def modo_apagado(self, item):
        indicator.set_icon_full(DISABLED, 'Icon disabled')
        logger.debug('Off')
        update_config('CONFIGURATION', 'application_on', '0')
        subprocess.Popen('pkexec slimbookbattery-pkexec apply'.split(' '))

        animations('0')

    def salir(self, item):
        os.system('pkexec slimbookbattery-pkexec service stop')
        Gtk.main_quit()


def animations(mode):
    code, stdout = subprocess.getstatusoutput('echo $XDG_CURRENT_DESKTOP | grep -i gnome')

    if code == 0:
        logger.info('Setting mode {} animations'.format(mode))
        if mode == '0':  # Application off
            logger.debug('Animations Active')
            os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')
        elif mode == '1':
            if config.getboolean('SETTINGS', 'ahorro_animations'):
                logger.debug('Animations Inactive')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
            else:
                logger.debug('Animations Active')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')

        elif mode == '2':
            if config.getboolean('SETTINGS', 'equilibrado_animations'):
                logger.debug('Animations Inactive')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
            else:
                logger.debug('Animations Active')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')

        elif mode == '3':
            if config.getboolean('SETTINGS', 'maxrendimiento_animations'):
                logger.debug('Animations Inactive')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
            else:
                logger.debug('Animations Active')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')
        else:
            logger.error('mode not found')
    else:
        logger.error('Not Gnome desktop {} {}'.format(code, stdout))


def reboot_process(process_name, path):
    logger.debug('Rebooting {} ...'.format(process_name))

    process = subprocess.getoutput('pgrep -f {}'.format(process_name))

    # If it find a process, kills it
    if len(process.split('\n')) > 1:
        proc_list = process.split('\n')

        for i in range(len(proc_list) - 1):
            code, stdout = subprocess.getstatusoutput('kill -9 {}'.format(proc_list[i]))
            logger.debug('Killing process {} Exit: {}'.format(proc_list[i], code))
            if code == 1:
                logger.error(stdout)

        logger.debug('Launching process...')
        if os.system('python3 {} &'.format(path)) == 0:
            logger.debug('Done')
        else:
            logger.debug("Couldn't launch process")


def rebootNvidia():
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=os.path.join(IMAGES_PATH, 'normal.png'),
        width=90,
        height=90,
        preserve_aspect_ratio=True)
    icon_MsgDialog = Gtk.Image.new_from_pixbuf(pixbuf)
    icon_MsgDialog.show()

    dialog = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,
                               buttons=Gtk.ButtonsType.YES_NO,
                               message_format=(_('Slimbook Battery')))
    dialog.set_image(icon_MsgDialog)
    dialog.format_secondary_text(
        _('The changes have been applied, but it is necessary to restart so that some of them may take effect.'
          ' Do you want to restart?'))
    response = dialog.run()
    if response == Gtk.ResponseType.YES:
        os.system('reboot')
    elif response == Gtk.ResponseType.NO:
        logger.info(_('System will not restart'))

    dialog.destroy()

    # Cada minuto va actualizando la información del porcentaje de carga que se verá al lado del icono del indicator
    # GLib.timeout_add(60000, change_label, indicator)


def update_config(section, variable, value):
    # We change our variable: config.set(section, variable, value)
    config.set(section, variable, str(value))

    # Writing our configuration file
    with open(config_file, 'w') as configfile:
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

    indicator = AppIndicator3.Indicator.new(APP_INDICATOR_ID, 'Slimbook Battery',
                                            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_icon_full(DISABLED, 'Icon disabled')

    Indicator()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
