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

from gi.repository import Gtk, GdkPixbuf, AppIndicator3, Notify as notify

user = utils.get_user()
_ = utils.load_translation('slimbookbattery')

IMAGES_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '../images'))

subprocess.getstatusoutput('echo $(date) @' + user + '>> /tmp/slimbookbattery.user')

user_home = os.path.expanduser('~{}'.format(user))

config_file = os.path.join(user_home, '.config/slimbookbattery/slimbookbattery.conf')
config = configparser.ConfigParser()
config.read(config_file)

ENERGY_SAVING = os.path.join(IMAGES_PATH, 'indicator/normal.png')
EQUILIBRADO = os.path.join(IMAGES_PATH, 'indicator/balanced_normal.png')
MAX_PERFORMANCE = os.path.join(IMAGES_PATH, 'indicator/performance_normal.png')

DISABLED = os.path.join(IMAGES_PATH, 'indicator/disabled_normal.png')

APPINDICATOR_ID = 'Slimbook Battery Indicator'

indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, 'Slimbook Battery',
                                        AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
indicator.set_icon_full(DISABLED, 'Icon disabled')

proceso = None
alert = None

IMAGES_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '..', 'images'))


if config['CONFIGURATION']['alerts'] == '1':
    if not os.path.isfile('/lib/systemd/system/slimbookbattery.service'):
        print('Creating notification service')
        os.system('pkexec slimbookbattery-pkexec service create')

    print('Opening notification service')

    os.system('pkexec slimbookbattery-pkexec service restart')

tdpcontroller = config['TDP']['tdpcontroller']


class Indicator(Gtk.Application):
    modo_actual = config['CONFIGURATION']['modo_actual']

    def __init__(self):

        if config['CONFIGURATION']['plug_warn'] == '1':
            check_plug()

        icono = int(config['CONFIGURATION']['icono'])
        if icono == 1:
            indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        elif icono == 0:
            indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

        indicator.set_menu(build_menu())
        notify.init(APPINDICATOR_ID)

        if int(config['CONFIGURATION']['application_on']) == 1:

            if os.system("pkexec slimbookbattery-pkexec autostart") == 0:
                print('Brightness set')

            # (avocado)
            # start_process(None)
            modo_actual = int(config['CONFIGURATION']['modo_actual'])

            if modo_actual == 1:
                indicator.set_icon_full(ENERGY_SAVING, 'Icon energy saving')

            elif modo_actual == 2:
                indicator.set_icon_full(EQUILIBRADO, 'Icon balanced')

            elif modo_actual == 3:
                indicator.set_icon_full(MAX_PERFORMANCE, 'Icon max performance')

        elif int(config['CONFIGURATION']['application_on']) == 0:
            print()

            indicator.set_icon_full(DISABLED, 'Icon energy saving')

        else:
            print(_("strappstatus4"))

        print()


def check_plug():
    last = config.get('CONFIGURATION', 'plugged')
    if not last == '':
        last = last.split('-')
        last_date = []
        for value in last:
            last_date.append(int(value))

        last_date = date(last_date[0], last_date[1], last_date[2])

        today = date.today()
        print(today)

        last_plug = abs(last_date - today).days

        if last_plug >= 15:
            status = (subprocess.getstatusoutput("cat /sys/class/power_supply/BAT0/status"))

            if status[0] == 0 and status[1] != 'Discharging':
                os.system('notify-send --icon ' + os.path.join(CURRENT_PATH,
                                                               '../images/normal.png') + ' "Slimbook Battery" "' +
                          _('It seems that you have been connected to AC for at least 15 days, we reccomend you to disconnect your charger, and discharge battery') + '"')
            else:
                print('Resetting last unplugged date')
                config.set('CONFIGURATION', 'plugged', str(date.today()))
                configfile = open(config_file, 'w')
                config.write(configfile)
                configfile.close()

        print('Time since last time disconnection: ' + str(last_plug) + ' days')
    else:
        print('No date saved')

        config.set('CONFIGURATION', 'plugged', str(date.today()))
        # This step is done at the end of function
        configfile = open(os.path.join(user_home, '.config/slimbookbattery/slimbookbattery.conf'), 'w')
        config.write(configfile)
        configfile.close()


def build_menu():
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
    item_modo1.connect('activate', modo_ahorro)
    item_modo1.set_image(icon_ahorro)
    item_modo1.set_always_show_image(True)

    item_modo2 = Gtk.ImageMenuItem()
    item_modo2.set_label(_('Balanced'))
    item_modo2.connect('activate', modo_equilibrado)
    item_modo2.set_image(icon_equilibrado)
    item_modo2.set_always_show_image(True)

    item_modo3 = Gtk.ImageMenuItem()
    item_modo3.set_label(_('Maximum Performance'))
    item_modo3.connect('activate', modo_max_rendimiento)
    item_modo3.set_image(icon_max_rendimiento)
    item_modo3.set_always_show_image(True)

    item_apagar = Gtk.ImageMenuItem()
    item_apagar.set_label(_('Off'))
    item_apagar.connect('activate', modo_apagado)
    item_apagar.set_image(icon_apagado)
    item_apagar.set_always_show_image(True)

    item_avanzado = Gtk.MenuItem()
    item_avanzado.set_label(_('Advanced mode'))
    item_avanzado.connect('activate', modo_avanzado)

    item_salir = Gtk.MenuItem()
    item_salir.set_label(_('Exit'))
    item_salir.connect('activate', salir)

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


def modo_ahorro(self):
    indicator.set_icon_full(ENERGY_SAVING, 'Icon energy saving')
    print('Battery Saving Mode')
    self.modo_actual = '1'
    update_config('CONFIGURATION', 'application_on', '1')
    update_config('CONFIGURATION', 'modo_actual', self.modo_actual)
    subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))

    controller_path = os.path.join('/usr/share/', tdpcontroller, 'src', tdpcontroller, 'indicator.py')
    reboot_process(tdpcontroller, controller_path)
    animations(self.modo_actual)


def modo_equilibrado(self):
    indicator.set_icon_full(EQUILIBRADO, 'Icon balanced')
    print('Normal power mode')
    self.modo_actual = '2'
    update_config('CONFIGURATION', 'application_on', '1')
    update_config('CONFIGURATION', 'modo_actual', self.modo_actual)
    subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))
    controller_path = os.path.join('/usr/share/', tdpcontroller, 'src', tdpcontroller, 'indicator.py')
    reboot_process(tdpcontroller, controller_path)
    animations(self.modo_actual)


def modo_max_rendimiento(self):
    indicator.set_icon_full(MAX_PERFORMANCE, 'Icon max performance')
    print('Full Power Mode')
    self.modo_actual = '3'
    update_config('CONFIGURATION', 'application_on', '1')
    update_config('CONFIGURATION', 'modo_actual', self.modo_actual)
    subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))

    controller_path = os.path.join('/usr/share/', tdpcontroller, 'src', tdpcontroller, 'indicator.py')
    reboot_process(tdpcontroller, controller_path)  # Only if it's running
    animations(self.modo_actual)


def modo_avanzado(self):
    print('preferencias')
    os.system(os.path.join(CURRENT_PATH, 'slimbookbatterypreferences.py'))


def modo_apagado(self):
    indicator.set_icon_full(DISABLED, 'Icon disabled')
    print('Off')
    update_config('CONFIGURATION', 'application_on', '0')
    subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))

    animations('0')


def animations(mode):
    check_desktop = subprocess.getstatusoutput('echo $XDG_CURRENT_DESKTOP | grep -i gnome')

    if check_desktop[0] == 0:
        print('Setting mode ' + mode + ' animations')
        if mode == '0':  # Application off
            print('Animations Active')
            os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
            os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')
        elif mode == '1':
            if config['SETTINGS']['ahorro_animations'] == "1":
                print('Animations Inactive')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
            else:
                print('Animations Active')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')

        elif mode == '2':
            if config['SETTINGS']['equilibrado_animations'] == '1':
                print('Animations Inactive')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
            else:
                print('Animations Active')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')

        elif mode == '3':
            if config['SETTINGS']['maxrendimiento_animations'] == '1':
                print('Animations Inactive')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
            else:
                print('Animations Active')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')
        else:
            print('mode not found')
    else:
        print('Not Gnome desktop ' + str(check_desktop[0]), check_desktop[1])


def salir(val):
    os.system('pkexec slimbookbattery-pkexec service stop')

    Gtk.main_quit()


def reboot_process(process_name, path):
    print('Rebooting ' + process_name + ' ...')

    process = subprocess.getoutput('pgrep -f ' + process_name)
    # print(process)

    # If it find a process, kills it
    if len(process.split('\n')) > 1:
        proc_list = process.split('\n')

        for i in range(len(proc_list) - 1):
            exit = subprocess.getstatusoutput('kill -9 ' + proc_list[i])
            print('Killing process ' + proc_list[i] + ' Exit: ' + str(exit[0]))
            if exit[0] == 1:
                print(exit[1])

        print('Launching process...')
        if os.system('python3 ' + path + '  &') == 0:
            print('Done')
        else:
            print("Couldn't launch process")


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
        _('The changes have been applied, but it is necessary to restart so that some of them may take effect. Do you want to restart?'))
    response = dialog.run()
    if response == Gtk.ResponseType.YES:
        os.system('reboot')
    elif response == Gtk.ResponseType.NO:
        print(_('System will not restart'))

    dialog.destroy()

    # Cada minuto va actualizando la información del porcentaje de carga que se verá al lado del icono del indicator
    # GLib.timeout_add(60000, change_label, indicator)


def update_config(section, variable, value):
    # We change our variable: config.set(section, variable, value)
    config.set(str(section), str(variable), str(value))

    # Writing our configuration file
    with open(config_file, 'w') as configfile:
        config.write(configfile)

    print("\n- Variable |" + variable + "| updated in .conf, actual value: " + value)


if __name__ == '__main__':
    Indicator()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
