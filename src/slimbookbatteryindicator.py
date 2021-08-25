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

import os
import gi
import signal
import sys
import subprocess
import configparser

from subprocess import PIPE
from multiprocessing import Event, Process
from threading import Thread
from os.path import expanduser

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, GdkPixbuf, AppIndicator3, Notify as notify

import gettext, locale

entorno_usu = locale.getlocale()[0]
if entorno_usu.find("en") >= 0 or entorno_usu.find("es") >= 0 or entorno_usu.find("it") >= 0 or entorno_usu.find("pt") >= 0 or entorno_usu.find("gl") >= 0:
	idiomas = [entorno_usu]
else:
	idiomas = ['en']

print('Slimbook Battery Indicator, executed as: '+str(subprocess.getoutput('whoami')))
print('Language: ', entorno_usu)



#Ruta del usuario actual
user_home = expanduser("~")

fichero_conf = user_home + '/.config/slimbookbattery/slimbookbattery.conf'
config = configparser.ConfigParser()
config.read(fichero_conf)

ENERGY_SAVING = '/usr/share/slimbookbattery/images/normal.png'
EQUILIBRADO = '/usr/share/slimbookbattery/images/balanced_normal.png'
MAX_PERFORMANCE = '/usr/share/slimbookbattery/images/performance_normal.png'

DISABLED = '/usr/share/slimbookbattery/images/disabled_normal.png'

STATUS_NORMAL = '/usr/share/slimbookbattery/images/normal.png'
STATUS_HIGH = '/usr/share/slimbookbattery/images/high.png'
STATUS_CRITICAL = '/usr/share/slimbookbattery/images/critical.png'

APPINDICATOR_ID = 'Slimbook Battery Indicator'

indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, '', AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
indicator.set_icon_full(DISABLED, 'Icon disabled')

proceso = None
alert = None

currpath = os.path.dirname(os.path.realpath(__file__))

t = gettext.translation('slimbookbattery',
                        currpath+'/locale',
                        languages=idiomas,
                        fallback=True,)

_ = t.gettext

if config['CONFIGURATION']['alerts'] == '1':
    if not os.path.isfile('/lib/systemd/system/slimbookbattery.service'):
        print('Creating notification service')
        os.system('pkexec slimbookbattery-pkexec service create')

    print('Opening notification service')

    os.system('pkexec slimbookbattery-pkexec service restart')

tdpcontroller = config['TDP']['tdpcontroller']

class Indicator():
    
    modo_actual = config['CONFIGURATION']['modo_actual']

    def __init__(self):

        icono = int(config['CONFIGURATION']['icono'])

        #Si el valor del icono obenido de la configuración es 1 nos mostrará el indicados de la aplicación para poder interactuar, en caso contrario estará oculto.
        if icono == 1:
            indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            #print('Icon: on')
        elif icono == 0:
            indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
            #print('Icon: off')

        indicator.set_menu(build_menu())
        notify.init(APPINDICATOR_ID)

        if int(config['CONFIGURATION']['application_on']) == 1 :

            if os.system("pkexec slimbookbattery-pkexec autostart") == 0:
                print('Brightness set')

            # (avocado)
            #start_process(None)
            modo_actual = int(config['CONFIGURATION']['modo_actual'])

            if modo_actual == 1:
                indicator.set_icon_full(ENERGY_SAVING, 'Icon energy saving')

            elif modo_actual == 2:
                indicator.set_icon_full(EQUILIBRADO, 'Icon balanced')

            elif modo_actual == 3:
                indicator.set_icon_full(MAX_PERFORMANCE, 'Icon max performance')

        elif int(config['CONFIGURATION']['application_on']) == 0 :
            print()

            indicator.set_icon_full(DISABLED, 'Icon energy saving')
                
            #print(_("strappstatus3"))

        else:
            print(_("strappstatus4"))

        print()


def build_menu():
    menu = Gtk.Menu()

    #Creación de los separadores
    item_separador1 = Gtk.SeparatorMenuItem()
    item_separador2 = Gtk.SeparatorMenuItem()
    item_separador3 = Gtk.SeparatorMenuItem()

    #Imagenes a utilizar para los iconos del menú
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='/usr/share/slimbookbattery/images/normal.png',
            width=25,
            height=25,
            preserve_aspect_ratio=True)
    icon_ahorro = Gtk.Image.new_from_pixbuf(pixbuf)


    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='/usr/share/slimbookbattery/images/balanced_normal.png',
            width=25,
            height=25,
            preserve_aspect_ratio=True)
    icon_equilibrado = Gtk.Image.new_from_pixbuf(pixbuf)

    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='/usr/share/slimbookbattery/images/performance_normal.png',
            width=25,
            height=25,
            preserve_aspect_ratio=True)
    icon_max_rendimiento = Gtk.Image.new_from_pixbuf(pixbuf)

    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='/usr/share/slimbookbattery/images/disabled_normal.png',
            width=25,
            height=25,
            preserve_aspect_ratio=True)
    icon_apagado = Gtk.Image.new_from_pixbuf(pixbuf)
    icon_apagado.set_pixel_size(24)

    #Creación de cada ImageMenuItem
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

    #Se añaden los items al menú en orden
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
    update_config('CONFIGURATION','application_on', '1')
    update_config('CONFIGURATION','modo_actual', self.modo_actual)
    child = subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))

    reboot_process(tdpcontroller, '/usr/share/'+tdpcontroller+'/src/'+tdpcontroller+'indicator.py')
    animations(self.modo_actual)

def modo_equilibrado(self):
    indicator.set_icon_full(EQUILIBRADO, 'Icon balanced')
    print('Normal power mode')
    self.modo_actual = '2'
    update_config('CONFIGURATION','application_on', '1')
    update_config('CONFIGURATION','modo_actual', self.modo_actual)
    child = subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))
    reboot_process(tdpcontroller, '/usr/share/'+tdpcontroller+'/src/'+tdpcontroller+'indicator.py')
    animations(self.modo_actual)

def modo_max_rendimiento(self):
    indicator.set_icon_full(MAX_PERFORMANCE, 'Icon max performance')
    print('Full Power Mode')
    self.modo_actual = '3'
    update_config('CONFIGURATION','application_on', '1')
    update_config('CONFIGURATION','modo_actual', self.modo_actual)
    child = subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))
    reboot_process(tdpcontroller, '/usr/share/'+tdpcontroller+'/src/'+tdpcontroller+'indicator.py') # Only if it's running
    animations(self.modo_actual)


def modo_avanzado(self):
    print('preferencias')
    os.system(currpath+'/slimbookbatterypreferences.py')

def modo_apagado(self):
    indicator.set_icon_full(DISABLED, 'Icon disabled')
    print('Off')
    update_config('CONFIGURATION','application_on', '0')
    subprocess.Popen(('pkexec slimbookbattery-pkexec apply').split(' '))
    
    animations('0')

def animations(mode):
        
    check_desktop = subprocess.getstatusoutput('echo $XDG_CURRENT_DESKTOP | grep -i gnome')
    
    if check_desktop[0] == 0:
        print('Setting mode '+mode+' animations')
        if mode == '0': # Application off
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
        print('Not Gnome desktop '+str(check_desktop[0]), check_desktop[1])

def salir(val):
    
    os.system('pkexec slimbookbattery-pkexec service stop')

    Gtk.main_quit()

def reboot_process(process_name, path):
    
    print('Rebooting '+process_name+' ...')

    process = subprocess.getoutput('pgrep -f '+process_name)
    #print(process)

    # If it find a process, kills it
    if len(process.split('\n'))>1:
        proc_list= process.split('\n')

        for i in range(len(proc_list)-1):
            exit = subprocess.getstatusoutput('kill -9 '+proc_list[i])
            print('Killing process '+ proc_list[i]+' Exit: '+str(exit[0]))
            if exit[0] == 1:
                print(exit[1])

        print('Launching process...')
        if os.system('python3 '+path+'  &') == 0:
            print('Done')
        else:
            print("Couldn't launch process")

def rebootNvidia():
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='/usr/share/slimbookbattery/images/normal.png',
            width=90,
            height=90,
            preserve_aspect_ratio=True)
    icon_MsgDialog = Gtk.Image.new_from_pixbuf(pixbuf)
    icon_MsgDialog.show()

    dialog = Gtk.MessageDialog(type= Gtk.MessageType.QUESTION,
        buttons= Gtk.ButtonsType.YES_NO,
        message_format=(_('Slimbook Battery')))
    dialog.set_image(icon_MsgDialog)
    dialog.format_secondary_text(_('The changes have been applied, but it is necessary to restart so that some of them may take effect.'))
    response = dialog.run()
    if response == Gtk.ResponseType.YES:
        os.system('reboot')
    elif response == Gtk.ResponseType.NO:
        print(_('System will not restart'))

    dialog.destroy()


    #Cada minuto va actualizando la información del porcentaje de carga que se verá al lado del icono del indicator
    #GLib.timeout_add(60000, change_label, indicator)

def update_config(section, variable, value):
    
    # We change our variable: config.set(section, variable, value)
    config.set(str(section), str(variable), str(value))

    # Writing our configuration file 
    with open(fichero_conf, 'w') as configfile:
        config.write(configfile)

    print("\n- Variable |"+variable+"| updated in .conf, actual value: "+value)


Indicator()

signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()