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
import getpass
import gettext
import locale
import math
import os
import subprocess
import time

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from os.path import expanduser

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

err_trace = []

user = getpass.getuser()
user_home = expanduser("~")
currpath = os.path.dirname(os.path.realpath(__file__))
imagespath = os.path.normpath(os.path.join(currpath, '..', 'images'))
config_file = user_home + '/.config/slimbookbattery/slimbookbattery.conf'

t = gettext.translation('preferences',
                        currpath + '/locale',
                        languages=idiomas,
                        fallback=True)

_ = t.gettext

if not os.path.isfile(config_file):
    pass

config = configparser.ConfigParser()
config.read(config_file)

class colors:  # You may need to change color settings
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    CYAN = "\033[1;36m"
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    BOLD = "\033[;1m"

class Preferences(Gtk.ApplicationWindow):

    min_resolution = False

    state_actual = ''
    autostart_inicial = ''
    modo_actual = ''
    workMode = ''
    icono_actual = ''

    def __init__(self):

        Gtk.Window.__init__(self, title=(_('Slimbook Battery Preferences')))

        self.get_style_context().add_class("bg-image")

        self.set_position(Gtk.WindowPosition.CENTER)  # // Allow movement

        self.set_size_request(1100, 400)

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_has_resize_grip(False)

        # Movement
        self.is_in_drag = False
        self.x_in_drag = 0
        self.y_in_drag = 0
        self.connect('button-press-event', self.on_mouse_button_pressed)
        self.connect('button-release-event', self.on_mouse_button_released)
        self.connect('motion-notify-event', self.on_mouse_moved)

        # Center
        # self.connect('realize', self.on_realize)

        self.child_process = subprocess.Popen(currpath + '/splash.py', stdout=subprocess.PIPE)

        try:
            self.set_ui()
        except Exception as e:
            print(e)
            self.child_process.terminate()

        print(str(self.get_size()))

    def on_realize(self, widget):
        monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
        scale = monitor.get_scale_factor()
        monitor_width = monitor.get_geometry().width / scale
        monitor_height = monitor.get_geometry().height / scale
        width = self.get_preferred_width()[0]
        height = self.get_preferred_height()[0]
        self.move((monitor_width - width) / 2, (monitor_height - height) / 2)

    def on_mouse_moved(self, widget, event):
        if self.is_in_drag:
            xi, yi = self.get_position()
            xf = int(xi + event.x_root - self.x_in_drag)
            yf = int(yi + event.y_root - self.y_in_drag)
            if math.sqrt(math.pow(xf - xi, 2) + math.pow(yf - yi, 2)) > 10:
                self.x_in_drag = event.x_root
                self.y_in_drag = event.y_root
                self.move(xf, yf)

    def on_mouse_button_released(self, widget, event):
        if event.button == 1:
            self.is_in_drag = False
            self.x_in_drag = event.x_root
            self.y_in_drag = event.y_root

    def on_mouse_button_pressed(self, widget, event):
        if event.button == 1:
            self.is_in_drag = True
            self.x_in_drag, self.y_in_drag = self.get_position()
            self.x_in_drag = event.x_root
            self.y_in_drag = event.y_root
            return True
        return False

    def set_ui(self):

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'normal.png'),
            width=825,
            height=225,
            preserve_aspect_ratio=True)

        self.set_default_icon(pixbuf)

        dimensiones = subprocess.getoutput("xdpyinfo | grep 'dimensions:'")
        dimensiones = dimensiones.split()
        dimensiones = dimensiones[1]
        dimensiones = dimensiones.split('x')

        ancho = dimensiones[0]
        alto = dimensiones[1]

        if (int(ancho) >= 1550) and (int(alto) >= 850):
            print(_('Full window is displayed'))
        else:
            self.resize(1100, 650)
            self.min_resolution = True

        win_grid = Gtk.Grid(column_homogeneous=True,
                            column_spacing=0,
                            row_spacing=20)

        self.add(win_grid)

        self.RestoreValues = Gtk.Button(label=(_('Restore default values')))
        self.RestoreValues.set_name('restore')
        self.RestoreValues.connect("clicked", self.on_buttonRestGeneral_clicked)
        self.RestoreValues.set_halign(Gtk.Align.END)

        self.btnCancel = Gtk.Button(label=(_('Cancel')))
        self.btnCancel.set_name('cancel')
        self.btnCancel.connect("clicked", self.close, 'x')
        self.btnCancel.set_halign(Gtk.Align.END)

        self.btnAccept = Gtk.Button(label=(_('Accept')))
        self.btnAccept.set_name('accept')
        self.btnAccept.connect("clicked", self.close_ok)
        self.btnAccept.set_halign(Gtk.Align.END)

        hbox = Gtk.Box()
        hbox.pack_start(self.btnCancel, True, True, 0)
        hbox.pack_start(self.RestoreValues, True, True, 0)
        hbox.pack_start(self.btnAccept, True, True, 0)
        hbox.set_halign(Gtk.Align.END)
        
        if self.min_resolution == True:
            hbox.set_name('smaller_label')
            
        label77 = Gtk.Label(label='')
        label77.set_halign(Gtk.Align.START)
        label77.set_name('version')
        version_line = subprocess.getstatusoutput("cat " + currpath + "/changelog |head -n1| egrep -o '\(.*\)'")
        if version_line[0] == 0:
            version = version_line[1]
            label77.set_markup('<span font="10">Version ' + version[1:len(version) - 1] + '</span>')
        label77.set_justify(Gtk.Justification.CENTER)

        win_grid.attach(hbox, 0, 4, 1, 1)
        win_grid.attach(label77, 0, 4, 1, 1)

        if subprocess.getstatusoutput('ls ' + user_home + '/.config/slimbookbattery/default/equilibrado')[0] != 0:
            print('Copiying configuration files ...')
            subprocess.getoutput('cp /usr/share/slimbookbattery/default ' + user_home + '/.config/slimbookbattery/')
            subprocess.getoutput('cp /usr/share/slimbookbattery/custom ' + user_home + '/.config/slimbookbattery/')

        # NOTEBOOK ***************************************************************

        notebook = Gtk.Notebook.new()
        if self.min_resolution == True:
            notebook.set_name('notebook_min')
        else:
            notebook.set_name('notebook')

        notebook.set_tab_pos(Gtk.PositionType.TOP)

        if self.min_resolution == True:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename = os.path.join(imagespath, 'slimbookbattery-header-2.png'),
                width = 775,
                height = 175,
                preserve_aspect_ratio = True)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename = os.path.join(imagespath, 'slimbookbattery-header-2.png'),
                width = 825,
                height = 225,
                preserve_aspect_ratio = True)

        logo = Gtk.Image.new_from_pixbuf(pixbuf)
        logo.set_halign(Gtk.Align.START)
        logo.set_valign(Gtk.Align.START)
        win_grid.attach(logo, 0, 0, 1, 4)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'cross.png'),
            width=20,
            height=20,
            preserve_aspect_ratio=True)

        close = Gtk.Image.new_from_pixbuf(pixbuf)
        close.set_name('close_button')

        evnt_close = Gtk.EventBox()
        evnt_close.add(close)
        evnt_close.set_halign(Gtk.Align.END)
        evnt_close.set_valign(Gtk.Align.START)
        evnt_close.connect('button-press-event', self.close)

        win_grid.attach(evnt_close, 0, 0, 1, 4)
        win_grid.attach(notebook, 0, 3, 1, 1)

        # GENERAL PAGE  **********************************************************

        print((_('Width: ')) + str(ancho) + ' ' + (_(' Height: ')) + str(alto))      

        general_page_grid = Gtk.Grid(column_homogeneous=True,
                                     column_spacing=0,
                                     row_spacing=20)

        general_grid = Gtk.Grid(column_homogeneous=True,
                                column_spacing=0,
                                row_spacing=25)

        general_page_grid.attach(general_grid, 0, 0, 1, 1)
        general_page_grid.set_halign(Gtk.Align.CENTER)

        # General page won't have scroll
        notebook.append_page(general_page_grid, Gtk.Label.new(_('General')))

        # ********* GENERAL PAGE COMPONENENTS ************************************

        # IMG 
        col_1 = 1
        col_2 = 3

        alignmet_1 = Gtk.Align.START
        alignmet_2 = Gtk.Align.START

        # LABEL ON/OFF (0, 0)
        label11 = Gtk.Label(label=_('Application On - Off:'))
        label11.set_halign(alignmet_1)
        general_grid.attach(label11, col_1, 0, 2, 1)

        # SWITCH (0, 1)
        self.switchOnOff = Gtk.Switch()
        self.switchOnOff.set_halign(alignmet_2)
        # self.switchOnOff.set_active(self.check_autostart_switchOnOff(self.switchOnOff))
        general_grid.attach(self.switchOnOff, col_2, 0, 1, 1)

        # LABEL AUTOSTART (1, 0)
        label11 = Gtk.Label(label=_('Autostart application:'))
        label11.set_halign(alignmet_1)
        general_grid.attach(label11, col_1, 1, 2, 1)

        # SWITCH (1, 1)
        self.switchAutostart = Gtk.Switch()
        self.switchAutostart.set_halign(alignmet_2)
        # self.switchAutostart.set_active(self.check_autostart_switchAutostart(self.switchAutostart))
        general_grid.attach(self.switchAutostart, col_2, 1, 1, 1)

        # LABEL DEVICE WORKING (3, 0)
        label11 = Gtk.Label(label=_('Working mode in case of battery failure'))
        label11.set_halign(alignmet_1)
        general_grid.attach(label11, col_1, 6, 2, 1)

        # DEVICES COMBO (3, 1)
        store = Gtk.ListStore(int, str)
        store.append([1, 'AC'])
        store.append([2, 'BAT'])

        self.comboBoxWorkMode = Gtk.ComboBox.new_with_model_and_entry(store)
        self.comboBoxWorkMode.set_entry_text_column(1)
        self.comboBoxWorkMode.set_halign(alignmet_2)

        if subprocess.getstatusoutput("cat /etc/tlp.conf | grep 'TLP_DEFAULT_MODE=AC'")[0] == 0:
            self.workMode = 'AC'
            self.comboBoxWorkMode.set_active(0)
        elif subprocess.getstatusoutput("cat /etc/tlp.conf | grep 'TLP_DEFAULT_MODE=BAT'")[0] == 0:
            self.workMode = 'BAT'
            self.comboBoxWorkMode.set_active(1)

        general_grid.attach(self.comboBoxWorkMode, col_2, 6, 1, 1)

        # LABEL INDICATOR (4, 0)
        hbox_indicator = Gtk.HBox(spacing=5)

        label11 = Gtk.Label(label=_('Icon on the taskbar (require restart app):'))

        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(
            _('Note: If you have the autostart activated and the icon hide, '
              'the app will be executed with the icon hide (once you restart the system)'))

        hbox_indicator.pack_start(label11, True, True, 0)
        hbox_indicator.pack_start(icon, True, True, 0)
        hbox_indicator.set_halign(alignmet_1)

        general_grid.attach(hbox_indicator, col_1, 4, 2, 1)

        # INDICATOR SWITCH (4, 1)
        self.switchIcon = Gtk.Switch()
        self.switchIcon.set_halign(alignmet_2)
        general_grid.attach(self.switchIcon, col_2, 4, 1, 1)

        # ***************** BUTTONS **********************************************

        buttons_grid = Gtk.Grid(column_homogeneous=True,
                                column_spacing=30,
                                row_spacing=20)
        buttons_grid.set_halign(Gtk.Align.CENTER)
        buttons_grid.set_name('radio_grid')

        general_grid.attach(buttons_grid, 0, 7, 5, 3)

        text = _('Actual energy mode:')
        label = Gtk.Label(label=text.upper())
        label.set_name('modes')
        buttons_grid.attach(label, 0, 0, 3, 1)

        # RADIOBUTTONS
        rbutton1 = Gtk.RadioButton.new_with_label_from_widget(None, (_('Energy Saving')))
        rbutton1.set_halign(Gtk.Align.CENTER)
        rbutton1.connect('toggled', self.on_button_toggled, '1')

        rbutton2 = Gtk.RadioButton.new_with_mnemonic_from_widget(rbutton1, (_('Balanced')))
        rbutton2.set_halign(Gtk.Align.CENTER)
        rbutton2.connect('toggled', self.on_button_toggled, '2')

        rbutton3 = Gtk.RadioButton.new_with_mnemonic_from_widget(rbutton1, (_('Maximum Performance')))
        rbutton3.set_halign(Gtk.Align.CENTER)
        rbutton3.connect('toggled', self.on_button_toggled, '3')

        # IMG LOW
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'normal.png'),
            width=100,
            height=100,
            preserve_aspect_ratio=True)
        mid_img = Gtk.Image.new_from_pixbuf(pixbuf)
        mid_img.set_halign(Gtk.Align.CENTER)
        mid_img.set_valign(Gtk.Align.START)

        buttons_grid.attach(mid_img, 0, 1, 1, 1)
        buttons_grid.attach(rbutton1, 0, 2, 1, 1)

        # IMG MEDIUM
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'balanced_normal.png'),
            width=100,
            height=100,
            preserve_aspect_ratio=True)
        mid_img = Gtk.Image.new_from_pixbuf(pixbuf)
        mid_img.set_halign(Gtk.Align.CENTER)
        mid_img.set_valign(Gtk.Align.START)

        buttons_grid.attach(mid_img, 1, 1, 1, 1)
        buttons_grid.attach(rbutton2, 1, 2, 1, 1)

        # IMG HIGH
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'performance_normal.png'),
            width=100,
            height=100,
            preserve_aspect_ratio=True)

        high_img = Gtk.Image.new_from_pixbuf(pixbuf)
        high_img.set_halign(Gtk.Align.CENTER)
        high_img.set_valign(Gtk.Align.START)

        buttons_grid.attach(high_img, 2, 1, 1, 1)
        buttons_grid.attach(rbutton3, 2, 2, 1, 1)

        self.load_components(rbutton1, rbutton2, rbutton3)

        # LOW MODE PAGE **********************************************************
        low_page_grid = Gtk.Grid(column_homogeneous=True,
                                 column_spacing=0,
                                 row_spacing=20)

        low_grid = Gtk.Grid(column_homogeneous=True,
                            row_homogeneous=False,
                            column_spacing=25,
                            row_spacing=20)
  
        low_page_grid.attach(low_grid, 0, 0, 2, 1)

        if self.min_resolution == True:
            scrolled_window1 = Gtk.ScrolledWindow()
            scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            
            scrolled_window1.set_min_content_height(400)
            scrolled_window1.set_min_content_width(1000)

            scrolled_window1.add_with_viewport(low_page_grid)
            notebook.append_page(scrolled_window1, Gtk.Label.new(_('Energy Saving')))
        else:
            notebook.append_page(low_page_grid, Gtk.Label.new(_('Energy Saving')))

        # ********* LOW MODE COMPONENTS COLUMN 1 *********************************
        print('\nLOADING LOW MODE COMPONENTS ...')

        label_width = 3
        label_width2 = 4
        scale_width = 2

        if self.min_resolution == True:
            label_col = 0
            button_col = 5
            label_col2 = 0
            button_col2 = 5
        else:
            label_col = 0
            button_col = 4
            label_col2 = 5
            button_col2 = 10
        row = 1

        # LABEL 0
        label33 = Gtk.Label(label='')
        label33.set_markup(
            '<big><b>' + (_('Battery mode parameters (disabled when you connect AC power):')) + '</b></big>')
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, 6, 1)

        # 1 ------------- CPU LIMITER *
        # LABEL 1
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        table_icon.set_valign(Gtk.Align.END)
        low_grid.attach(table_icon, 0, row, label_width, 1)
        label33 = Gtk.Label(label=_('Limit CPU profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'warning.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this setting affects to performance'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 1
        store = Gtk.ListStore(int, str)
        store.append([1, (_('maximum'))])
        store.append([2, (_('medium'))])
        store.append([3, (_('none'))])
        self.comboBoxLimitCPU = Gtk.ComboBox.new_with_model_and_entry(store)
        self.comboBoxLimitCPU.set_valign(Gtk.Align.CENTER)
        self.comboBoxLimitCPU.set_halign(Gtk.Align.END)
        self.comboBoxLimitCPU.set_entry_text_column(1)

        config.read(user_home + '/.config/slimbookbattery/slimbookbattery.conf')

        value = config['SETTINGS']['limit_cpu_ahorro']

        if value == '1':  # Max
            self.comboBoxLimitCPU.set_active(0)
        elif value == '2':  # Mid
            self.comboBoxLimitCPU.set_active(1)
        elif value == '3':  # None
            self.comboBoxLimitCPU.set_active(2)

        low_grid.attach(self.comboBoxLimitCPU, button_col - 1, row, scale_width, 1)
        # 2 ------------- CPU GOVERNOR *
        # LABEL 2
        governorCompatible, governor_name = governorIsCompatible()
        if governorCompatible:
            row = row + 1

            # LABEL 2
            label33 = Gtk.Label(label=_('CPU scaling governor saving profile:'))
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col, row, label_width, 1)

            # BUTTON 2
            store = Gtk.ListStore(int, str)

            store.append([1, 'powersave'])  # aureo

            self.comboBoxGovernor = Gtk.ComboBox.new_with_model_and_entry(store)
            self.comboBoxGovernor.set_valign(Gtk.Align.CENTER)
            self.comboBoxGovernor.set_halign(Gtk.Align.END)
            self.comboBoxGovernor.set_entry_text_column(1)
            self.comboBoxGovernor.set_active(0)
            self.comboBoxGovernor.set_sensitive(False)
            low_grid.attach(self.comboBoxGovernor, button_col - 1, row, scale_width, 1)
        # 3 ------------- GRAPHICS SAVING *
        # LABEL 3
        row = row + 1
        # (3, 0)
        label33 = Gtk.Label(label=_('Graphic card saving profile (Nvidia-AMD-Intel):'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 3
        self.switchGraphics = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchGraphics.set_name('ahorrodeenergia')

        self.check_autostart_Graphics(self.switchGraphics)

        config.read(user_home + '/.config/slimbookbattery/slimbookbattery.conf')

        low_grid.attach(self.switchGraphics, button_col, row, 1, 1)
        # 4 ------------- SOUND SAVING *
        # LABEL 3
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col, row, label_width, 1)
        label33 = Gtk.Label(label=_('Sound power saving profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this setting can cause slight clicks in sound output'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 4
        self.switchSound = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchSound.set_name('ahorrodeenergia')
        self.check_autostart_switchSound(self.switchSound)

        low_grid.attach(self.switchSound, button_col, row, 1, 1)
        # 5 ------------- WIFI SAVING *
        # LABEL 5
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col, row, label_width, 1)
        label33 = Gtk.Label(label=_('Wi-Fi power saving profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: power save can cause an unstable wifi connection.'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 5
        self.switchWifiPower = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiPower.set_name('ahorrodeenergia')
        self.check_autostart_switchWifiPower(self.switchWifiPower)

        low_grid.attach(self.switchWifiPower, button_col, row, 1, 1)
        # 6 ------------- DISABLE BLUETOOTH IF NOT IN USE *
        # LABEL 6
        row = row + 1
        label33 = Gtk.Label(label=_('Bluetooth disabled when not in use:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 6
        self.switchBluetoothNIU = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBluetoothNIU.set_valign(Gtk.Align.CENTER)
        self.switchBluetoothNIU.set_name('ahorrodeenergia')
        self.check_switchBluetooth(self.switchBluetoothNIU)

        low_grid.attach(self.switchBluetoothNIU, button_col, row, 1, 1)
        # 7 ------------- DISABLE WIFI IF NOT IN USE *
        # LABEL 7
        row = row + 1
        label33 = Gtk.Label(label=_('Wi-Fi disabled when not in use:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 7
        self.switchWifiNIU = Gtk.Switch()
        self.switchWifiNIU.set_name('ahorrodeenergia')
        self.switchWifiNIU.set_halign(Gtk.Align.END)
        self.switchWifiNIU.set_valign(Gtk.Align.CENTER)
        self.check_autostart_switchWifiNIU(self.switchWifiNIU)
        low_grid.attach(self.switchWifiNIU, button_col, row, 1, 1)
        # 8 ------------- TDP ADJUST
        tdpcontroller = config['TDP']['tdpcontroller']
        if config['TDP']['tdpcontroller'] == '':

            proc = subprocess.getstatusoutput("cat /proc/cpuinfo | grep 'model name' | head -n1")
            if  proc[0] == 0 :
                if proc[1].find('intel'):
                    tdpcontroller = 'slimbookintelcontroller'
                elif proc[1].find('amd'):
                    tdpcontroller = 'slimbookamdcontroller'
                else:
                    print('Could not find TDP contoller for your processor')

                config.set('TDP', 'tdpcontroller', tdpcontroller)
                
                print('TDP Controller found: '+tdpcontroller)

                # This step is done at the end of function
                configfile = open(user_home + '/.config/slimbookbattery/slimbookbattery.conf', 'w')
                config.write(configfile)
                configfile.close()

        if tdpcontroller != '':

            row = row + 2
            label33 = Gtk.Label(label='')
            label33.set_markup('<big><b>' + (_('CPU TDP Settings')) + '</b></big>')
            if self.min_resolution == True:
                label33.set_name('title')
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col, row, 4, 1)

            if subprocess.getstatusoutput('which ' + tdpcontroller)[0] == 0:  # if TDP controller is installed
                # print('Found '+tdpcontroller)
                # LABEL 7
                row = row + 1
                label33 = Gtk.Label(label=_('Synchronice battery mode with TDP mode:'))
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

                # BUTTON 7
                self.switchTDP = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                self.switchTDP.set_name('saving_tdpsync')
                self.check_autostart_switchTDP(self.switchTDP)
                low_grid.attach(self.switchTDP, button_col, row, 1, 1)
                # print(tdpcontroller)
            else:
                print('TDP Controller not installed')
                # LABEL 7
                row = row + 1
                label33 = Gtk.Label(label=_('Synchronice battery mode with TDP mode:'))
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

                # BUTTON 7
                self.switchTDP = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                self.switchTDP.set_name('saving_tdpsync')

                self.switchTDP.set_sensitive(False)
                # self.check_autostart_switchTDP(self.switchTDP)
                low_grid.attach(self.switchTDP, button_col, row, 1, 1)

                # LABEL 7
                row = row + 1
                self.link = ''
                if tdpcontroller == 'slimbookintelcontroller':
                    if idiomas[0].find('es') != -1:
                        self.link = 'https://slimbook.es/es/tutoriales/aplicaciones-slimbook/515-slimbook-intel-controller'
                    else:
                        print(idiomas)
                        self.link = 'https://slimbook.es/en/tutoriales/aplicaciones-slimbook/514-en-slimbook-intel-controller'
                else:
                    if idiomas[0].find('es') != -1:
                        self.link = 'https://slimbook.es/es/tutoriales/aplicaciones-slimbook/493-slimbook-amd-controller'
                    else:
                        print(idiomas)
                        self.link = 'https://slimbook.es/en/tutoriales/aplicaciones-slimbook/494-slimbook-amd-controller-en'

                label33 = Gtk.Label()
                label33.set_markup("<a href='" + self.link + "'>" + _('Learn more about TDP Controller') + "</a>")
                label33.set_name('link')
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)
                # print(tdpcontroller)

        # ********* LOW MODE COMPONENTS COLUMN 2 *********************************

        if not self.min_resolution == True:
            row = 1
        else:
            row = row+1

        label33 = Gtk.Label(label='')
        label33.set_markup('<big><b>' + (_('Persistent changes:')) + '</b></big>')
        if self.min_resolution == True:
            label33.set_name('title')
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, 5, 1)
        # 1 ------------- BRIGHTNESS *
        # LABEL 1
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        table_icon.set_valign(Gtk.Align.END)
        low_grid.attach(table_icon, label_col2, row, label_width2 - 1, 1)
        label33 = Gtk.Label(label=_('Set screen brightness:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this option reduces the battery consumption considerably'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 1

        self.scaleBrightness = Gtk.Scale()
        ahorroBrightness = config['SETTINGS']['ahorro_brightness']
        self.scaleBrightness.set_adjustment(Gtk.Adjustment.new(int(ahorroBrightness), 00, 100, 5, 5, 0))
        self.scaleBrightness.set_digits(0)
        self.scaleBrightness.set_hexpand(True)

        self.brightness_switch1 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.END)
        self.brightness_switch1.set_name('saving_brightness_switch')

        self.brightness_switch1.connect("state-set", self.brightness_switch_changed, self.scaleBrightness)
        self.check_autostart_switchBrightness(self.brightness_switch1, self.scaleBrightness)

        low_grid.attach(self.brightness_switch1, button_col2, row, 1, 1)
        low_grid.attach(self.scaleBrightness, button_col2 - 2, row, scale_width, 1)

        exec = subprocess.getstatusoutput('echo $XDG_CURRENT_DESKTOP | grep -i gnome')
        if exec[0] == 0:
            row = row + 1
            # print('Gnome')
            # LABEL 2
            label33 = Gtk.Label(label=_('Disable animations:'))
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col2, row, label_width2, 1)
            # BUTTON 2
            self.switchAnimations = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
            self.switchAnimations.set_name('ahorro_animations')

            self.check_autostart_switchAnimations(self.switchAnimations)

            low_grid.attach(self.switchAnimations, button_col2, row, 1, 1)

        row = row + 1
        # 3 ------------- DISABLE BLUETOOTH ON STARTUP *
        # LABEL 3
        label33 = Gtk.Label(label=_("Bluetooth does not boot on start:"))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 3
        self.switchBluetoothOS = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBluetoothOS.set_name('ahorrodeenergia')

        self.check_switchBluetoothOS(self.switchBluetoothOS)

        # self.switchBluetoothOS.set_active(self.check_autostart_switchBluetoothOS(self.switchBluetoothOS))
        low_grid.attach(self.switchBluetoothOS, button_col2, row, 1, 1)

        row = row + 1
        # 4 ------------- DISABLE WIFI ON STARTUP *
        # LABEL 4
        label33 = Gtk.Label(label=_("Wi-Fi does not boot on start:"))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 4
        self.switchWifiOS = Gtk.Switch()
        self.switchWifiOS.set_name('ahorrodeenergia')
        self.switchWifiOS.set_halign(Gtk.Align.END)
        self.switchWifiOS.set_valign(Gtk.Align.CENTER)
        self.check_autostart_switchWifiOS(self.switchWifiOS)

        low_grid.attach(self.switchWifiOS, button_col2, row, 1, 1)

        row = row + 1
        # 5 ------------- DISABLE WIFI WHEN LAN *
        # LABEL 5
        label33 = Gtk.Label(label=_('Disable Wi-Fi when LAN is connected:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 5
        self.switchWifiDisableLAN = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiDisableLAN.set_name('ahorrodeenergia')
        self.check_autostart_switchDisableLAN(self.switchWifiDisableLAN)
        low_grid.attach(self.switchWifiDisableLAN, button_col2, row, 1, 1)

        row = row + 1

        # 6 ------------- USB AUTOSUSPENSION
        # LABEL 6
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col2, row, label_width2, 1)
        label33 = Gtk.Label(label=_('Autosuspend USB Ports:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(
            _('Note: Set autosuspend mode for all USB devices upon system start or a change of power source. '
              'Input devices like mice and keyboards as well as scanners are excluded by default'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 6
        self.switchUSBSuspend = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchUSBSuspend.set_name('ahorrodeenergia')

        self.check_autostart_USBSuspend(self.switchUSBSuspend)
        low_grid.attach(self.switchUSBSuspend, button_col2, row, 1, 1)

        row = row + 1
        # 7 ------------- AUTOSUSPENSION EXCLUDED IDS
        # LABEL 7
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col2, row, label_width2, 1)
        label33 = Gtk.Label(label=_('Excluded USB IDs from USB autosuspend:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        # Se leen los diferentes USB que hay disponibles y se almacenan en un archivo temporalmente

        if os.system('lsusb | grep ID >> ' + user_home + '/.config/slimbookbattery/usbidlist') == 0:
            try:
                USBIDsList = ''
                # Se lee el archivo temporal que se ha creado y
                # se va sacando para que solo nos muestre el ID junto con el nombre del USB
                f = open(user_home + '/.config/slimbookbattery/usbidlist', 'r')
                line = f.readline()
                while line:
                    lineaActual = line
                    # Saca la posición del ID en la linea
                    IDPos = lineaActual.find("ID")
                    # Saca la última posición de la linea
                    longitud = len(lineaActual) - 1
                    # Una vez teniendo estas 2 posiciones ya tenemos el ID junto con el nombre del USB
                    # y se concatena al string USBIDsList
                    USBIDsList = USBIDsList + lineaActual[IDPos:longitud] + '\n'
                    line = f.readline()
                f.close()

                # Se elimina el archivo temporal
                os.system('rm ' + user_home + '/.config/slimbookbattery/usbidlist')
            except Exception:
                print('USB ID list 403')
        else:
            print('USB ID list 404')

        # En este tooltip
        msg = _('Note: You need to write in the Text Box the USB IDs '
                '(separate with spaces) to exclude from autosuspend')
        icon.set_tooltip_text(msg + '.\n\n' + USBIDsList)
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 7
        self.entryBlacklistUSBIDs = Gtk.Entry(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        if self.switchUSBSuspend.get_active():
            self.entryBlacklistUSBIDs.set_sensitive(True)
        else:
            self.entryBlacklistUSBIDs.set_sensitive(False)
        self.entryBlacklistUSBIDs.set_text(str(self.gen_blacklist('ahorrodeenergia')))

        low_grid.attach(self.entryBlacklistUSBIDs, button_col2 - 1, row, scale_width, 1)

        row = row + 1
        # 8 ------------- EXCLUDE BLUETOOTH *
        # LABEL 8
        label44 = Gtk.Label(label=_('Exclude bluetooth devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)
        # BUTTON 8
        self.switchBlacklistBUSB = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBlacklistBUSB.set_valign(Gtk.Align.CENTER)
        self.switchBlacklistBUSB.set_name('ahorrodeenergia')
        self.check_autostart_BlacklistBUSB(self.switchBlacklistBUSB)

        low_grid.attach(self.switchBlacklistBUSB, button_col2, row, 1, 1)

        row = row + 1
        # 9 ------------- EXCLUDE PRINTERS *
        # LABEL 9
        label44 = Gtk.Label(label=_('Exclude printer devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 9
        self.switchBlacklistPrintUSB = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBlacklistPrintUSB.set_name('ahorrodeenergia')
        self.check_autostart_BlacklistPrintUSB(self.switchBlacklistPrintUSB)

        low_grid.attach(self.switchBlacklistPrintUSB, button_col2, row, 1, 1)

        row = row + 1
        # 10 ------------ EXCLUDE NET DEVICES *
        # LABEL 10
        label44 = Gtk.Label(label=_('Exclude Ethernet devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 10
        self.switchBlacklistWWANUSB = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBlacklistWWANUSB.set_name('ahorrodeenergia')

        self.check_autostart_BlacklistWWANUSB(self.switchBlacklistWWANUSB)

        low_grid.attach(self.switchBlacklistWWANUSB, button_col2, row, 1, 1)

        row = row + 1
        # 11 ------------ DISABLE USB AUTOSUSPENSION ON SHUTDOWN *
        # LABEL 11
        label44 = Gtk.Label(label=_('Disable USB autosuspend mode upon system shutdown:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 11
        self.switchShutdownSuspendUSB = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchShutdownSuspendUSB.set_name('ahorrodeenergia')

        self.check_autostart_ShutdownSuspendUSB(self.switchShutdownSuspendUSB)

        low_grid.attach(self.switchShutdownSuspendUSB, button_col2, row, 1, 1)

        # Connections
        self.switchUSBSuspend.connect("notify::active", self.on_switchUSBSuspend_change, self.entryBlacklistUSBIDs,
                                      self.switchBlacklistBUSB, self.switchBlacklistPrintUSB,
                                      self.switchBlacklistWWANUSB, self.switchShutdownSuspendUSB)
        self.on_switchUSBSuspend_change(self.switchUSBSuspend, 'x', self.entryBlacklistUSBIDs, self.switchBlacklistBUSB,
                                        self.switchBlacklistPrintUSB, self.switchBlacklistWWANUSB,
                                        self.switchShutdownSuspendUSB)

        # MID MODE PAGE **********************************************************

        low_page_grid = Gtk.Grid(column_homogeneous=True,
                                 column_spacing=0,
                                 row_spacing=20)

        low_grid = Gtk.Grid(column_homogeneous=True,
                            row_homogeneous=False,
                            column_spacing=25,
                            row_spacing=20)

        low_page_grid.attach(low_grid, 0, 0, 2, 4)

        if self.min_resolution == True:
            scrolled_window1 = Gtk.ScrolledWindow()
            scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            
            scrolled_window1.set_min_content_height(400)
            scrolled_window1.set_min_content_width(1000)

            scrolled_window1.add_with_viewport(low_page_grid)
            notebook.append_page(scrolled_window1, Gtk.Label.new(_('Balanced')))
        else:
            notebook.append_page(low_page_grid, Gtk.Label.new(_('Balanced')))

        # ********* MID MODE COMPONENTS COLUMN 1 *********************************
        print('\nLOADING BALANCED MODE COMPONENTS ...')

        row = 1

        # LABEL 0
        label33 = Gtk.Label(label='')
        label33.set_markup(
            '<big><b>' + (_('Battery mode parameters (disabled when you connect AC power):')) + '</b></big>')
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, 6, 1)
        # 1 ------------- CPU LIMITER *
        # LABEL 1
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        table_icon.set_valign(Gtk.Align.END)
        low_grid.attach(table_icon, 0, row, label_width, 1)
        label33 = Gtk.Label(label=_('Limit CPU profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'warning.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this setting affects to performance'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 1
        store = Gtk.ListStore(int, str)
        store.append([1, (_('maximum'))])
        store.append([2, (_('medium'))])
        store.append([3, (_('none'))])
        self.comboBoxLimitCPU2 = Gtk.ComboBox.new_with_model_and_entry(store)
        self.comboBoxLimitCPU2.set_valign(Gtk.Align.CENTER)
        self.comboBoxLimitCPU2.set_halign(Gtk.Align.END)
        self.comboBoxLimitCPU2.set_entry_text_column(1)

        value = config['SETTINGS']['limit_cpu_equilibrado']

        if value == '1':
            self.comboBoxLimitCPU2.set_active(0)
        elif value == '2':
            self.comboBoxLimitCPU2.set_active(1)
        elif value == '3':
            self.comboBoxLimitCPU2.set_active(2)

        low_grid.attach(self.comboBoxLimitCPU2, button_col - 1, row, scale_width, 1)
        # 2 ------------- CPU GOVERNOR *
        # LABEL 2
        governorCompatible, governor_name = governorIsCompatible()
        if governorCompatible:
            row = row + 1

            # LABEL 2
            label33 = Gtk.Label(label=_('CPU scaling governor saving profile:'))
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col, row, label_width, 1)

            # BUTTON 2
            store = Gtk.ListStore(int, str)
            if governor_name == 'intel_pstate':
                store.append([1, 'powersave'])
                store.append([2, 'performance'])
            elif governor_name == 'acpi-cpufreq':
                store.append([1, 'ondemand'])
                store.append([2, 'schedutil'])
                store.append([3, 'powersave'])
                store.append([4, 'performance'])
                store.append([5, 'conservative'])

            self.comboBoxGovernor2 = Gtk.ComboBox.new_with_model_and_entry(store)
            self.comboBoxGovernor2.set_name('equilibrado')
            self.comboBoxGovernor2.set_valign(Gtk.Align.CENTER)
            self.comboBoxGovernor2.set_halign(Gtk.Align.END)
            self.comboBoxGovernor2.set_entry_text_column(1)
            self.check_autostart_Governor(self.comboBoxGovernor2, governor_name)

            low_grid.attach(self.comboBoxGovernor2, button_col - 1, row, scale_width, 1)
        # 3 ------------- GRAPHICS SAVING *
        # LABEL 3
        row = row + 1
        # (3, 0)
        label33 = Gtk.Label(label=_('Graphic card saving profile (Nvidia-AMD-Intel):'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 3
        self.switchGraphics2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchGraphics2.set_name('equilibrado')

        self.check_autostart_Graphics(self.switchGraphics2)

        low_grid.attach(self.switchGraphics2, button_col, row, 1, 1)
        # 4 ------------- SOUND SAVING *
        # LABEL 4
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col, row, label_width, 1)
        label33 = Gtk.Label(label=_('Sound power saving profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this setting can cause slight clicks in sound output'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 4
        self.switchSound2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchSound2.set_name('equilibrado')

        self.check_autostart_switchSound(self.switchSound2)
        low_grid.attach(self.switchSound2, button_col, row, 1, 1)
        # 5 ------------- WIFI SAVING *
        # LABEL 5
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col, row, label_width, 1)
        label33 = Gtk.Label(label=_('Wi-Fi power saving profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: power save can cause an unstable wifi connection.'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 5
        self.switchWifiPower2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiPower2.set_name('equilibrado')

        self.check_autostart_switchWifiPower(self.switchWifiPower2)
        low_grid.attach(self.switchWifiPower2, button_col, row, 1, 1)
        # 6 ------------- DISABLE BLUETOOTH IF NOT IN USE *
        # LABEL 6
        row = row + 1
        label33 = Gtk.Label(label=_('Bluetooth disabled when not in use:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 6
        self.switchBluetoothNIU2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBluetoothNIU2.set_name('equilibrado')

        self.switchBluetoothNIU2.set_valign(Gtk.Align.CENTER)
        self.check_switchBluetooth(self.switchBluetoothNIU2)
        low_grid.attach(self.switchBluetoothNIU2, button_col, row, 1, 1)
        # 7 ------------- DISABLE WIFI IF NOT IN USE *
        # LABEL 7
        row = row + 1
        label33 = Gtk.Label(label=_('Wi-Fi disabled when not in use:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 7
        self.switchWifiNIU2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiNIU2.set_name('equilibrado')

        self.switchWifiNIU2.set_valign(Gtk.Align.CENTER)
        self.check_autostart_switchWifiNIU(self.switchWifiNIU2)
        low_grid.attach(self.switchWifiNIU2, button_col, row, 1, 1)
        # 8 ------------- TDP ADJUST
 
        if tdpcontroller != '':
            row = row + 2
            label33 = Gtk.Label(label='')
            label33.set_markup('<big><b>' + (_('CPU TDP Settings')) + '</b></big>')
            if self.min_resolution == True:
                label33.set_name('title')
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col, row, 4, 1)

            if subprocess.getstatusoutput('which ' + tdpcontroller)[0] == 0:  # if TDP controller is installed
                # LABEL 7
                row = row + 1
                label33 = Gtk.Label(label=_('Synchronice battery mode with TDP mode:'))
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

                # BUTTON 7
                self.switchTDP2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                self.switchTDP2.set_name('balanced_tdpsync')

                self.check_autostart_switchTDP(self.switchTDP2)
                low_grid.attach(self.switchTDP2, button_col, row, 1, 1)
                # print(tdpcontroller)
            else:
                print('TDP Controller not installed')
                # LABEL 7
                row = row + 1
                label33 = Gtk.Label(label=_('Synchronice battery mode with TDP mode:'))
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

                # BUTTON 7
                self.switchTDP2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                self.switchTDP2.set_name('balanced_tdpsync')
                self.switchTDP2.set_sensitive(False)
                # self.check_autostart_switchTDP(self.switchTDP)
                low_grid.attach(self.switchTDP2, button_col, row, 1, 1)

                row = row + 1
                label33 = Gtk.Label()
                label33.set_markup("<a href='" + self.link + "'>" + _('Learn more about TDP Controller') + "</a>")
                label33.set_name('link')
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

        # ********* MID MODE COMPONENTS COLUMN 2 *********************************

        if not self.min_resolution == True:
            row = 1
        else:
            row = row+1

        label33 = Gtk.Label(label='')
        label33.set_markup('<big><b>' + (_('Persistent changes:')) + '</b></big>')
        if self.min_resolution == True:
            label33.set_name('title')
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, 5, 1)
        # 1 ------------- BRIGHTNESS *
        # LABEL 1
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        table_icon.set_valign(Gtk.Align.END)
        low_grid.attach(table_icon, label_col2, row, label_width2 - 1, 1)
        label33 = Gtk.Label(label=_('Set screen brightness:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this option reduces the battery consumption considerably'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 1
        self.scaleBrightness2 = Gtk.Scale()
        equilibradoBrightness = config['SETTINGS']['equilibrado_brightness']
        self.scaleBrightness2.set_adjustment(Gtk.Adjustment.new(int(equilibradoBrightness), 0, 100, 5, 5, 0))
        self.scaleBrightness2.set_digits(0)
        self.scaleBrightness2.set_hexpand(True)

        self.brightness_switch2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.END)
        self.brightness_switch2.set_name('balanced_brightness_switch')

        self.brightness_switch2.connect("state-set", self.brightness_switch_changed, self.scaleBrightness2)
        self.check_autostart_switchBrightness(self.brightness_switch2, self.scaleBrightness2)

        low_grid.attach(self.scaleBrightness2, button_col2 - 2, row, scale_width, 1)
        low_grid.attach(self.brightness_switch2, button_col2, row, 1, 1)

        if subprocess.getstatusoutput('echo $XDG_CURRENT_DESKTOP | grep -i gnome')[0] == 0:
            row = row + 1
            # LABEL 2
            label33 = Gtk.Label(label=_('Disable animations:'))
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col2, row, label_width2, 1)
            # BUTTON 2
            self.switchAnimations2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
            self.switchAnimations2.set_name('equilibrado_animations')

            self.check_autostart_switchAnimations(self.switchAnimations2)
            low_grid.attach(self.switchAnimations2, button_col2, row, 1, 1)

        row = row + 1
        # 3 ------------- DISABLE BLUETOOTH ON STARTUP *
        # LABEL 3
        label33 = Gtk.Label(label=_("Bluetooth does not boot on start:"))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 3
        self.switchBluetoothOS2 = Gtk.Switch()
        self.switchBluetoothOS2.set_valign(Gtk.Align.CENTER)
        self.switchBluetoothOS2.set_name('equilibrado')
        self.switchBluetoothOS2.set_halign(Gtk.Align.END)
        self.check_switchBluetoothOS(self.switchBluetoothOS2)

        low_grid.attach(self.switchBluetoothOS2, button_col2, row, 1, 1)

        row = row + 1
        # 4 ------------- DISABLE WIFI ON STARTUP *
        # LABEL 4
        label33 = Gtk.Label(label=_("Wi-Fi does not boot on start:"))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 4
        self.switchWifiOS2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiOS2.set_name('equilibrado')

        self.check_autostart_switchWifiOS(self.switchWifiOS2)
        low_grid.attach(self.switchWifiOS2, button_col2, row, 1, 1)

        row = row + 1
        # 5 ------------- DISABLE WIFI WHEN LAN *
        # LABEL 5
        label33 = Gtk.Label(label=_('Disable Wi-Fi when LAN is connected:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 5
        self.switchWifiDisableLAN2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiDisableLAN2.set_name('equilibrado')

        self.check_autostart_switchDisableLAN(self.switchWifiDisableLAN2)
        low_grid.attach(self.switchWifiDisableLAN2, button_col2, row, 1, 1)

        row = row + 1
        # 6 ------------- USB AUTOSUSPENSION *
        # LABEL 6
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col2, row, label_width2, 1)
        label33 = Gtk.Label(label=_('Autosuspend USB Ports:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(
            _('Note: Set autosuspend mode for all USB devices upon system start or a change of power source. '
              'Input devices like mice and keyboards as well as scanners are excluded by default'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 6
        self.switchUSBSuspend2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchUSBSuspend2.set_name('equilibrado')
        self.check_autostart_USBSuspend(self.switchUSBSuspend2)
        low_grid.attach(self.switchUSBSuspend2, button_col2, row, 1, 1)

        row = row + 1
        # 7 ------------- AUTOSUSPENSION EXCLUDED IDS *
        # LABEL 7
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col2, row, label_width2, 1)
        label33 = Gtk.Label(label=_('Excluded USB IDs from USB autosuspend:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        # Se leen los diferentes USB que hay disponibles y se almacenan en un archivo temporalmente

        if os.system('lsusb | grep ID >> ' + user_home + '/.config/slimbookbattery/usbidlist') == 0:
            try:
                USBIDsList = ''
                # Se lee el archivo temporal que se ha creado y se va sacando
                # para que solo nos muestre el ID junto con el nombre del USB
                f = open(user_home + '/.config/slimbookbattery/usbidlist', 'r')
                line = f.readline()
                while line:
                    lineaActual = line
                    # Saca la posición del ID en la linea
                    IDPos = lineaActual.find("ID")
                    # Saca la última posición de la linea
                    longitud = len(lineaActual) - 1
                    # Una vez teniendo estas 2 posiciones ya tenemos el ID
                    # junto con el nombre del USB y se concatena al string USBIDsList
                    USBIDsList = USBIDsList + lineaActual[IDPos:longitud] + '\n'
                    line = f.readline()
                f.close()

                # Se elimina el archivo temporal
                os.system('rm ' + user_home + '/.config/slimbookbattery/usbidlist')
            except Exception:
                print('USB ID list 403')
        else:
            print('USB ID list 404')

        # En este tooltip
        msg = _('Note: You need to write in the Text Box the USB IDs (separate with spaces) '
                'to exclude from autosuspend')
        icon.set_tooltip_text(msg + '.\n\n' + USBIDsList)
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 7
        self.entryBlacklistUSBIDs2 = Gtk.Entry(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        if self.switchUSBSuspend2.get_active():
            self.entryBlacklistUSBIDs2.set_sensitive(True)
        else:
            self.entryBlacklistUSBIDs2.set_sensitive(False)
        self.entryBlacklistUSBIDs2.set_text(str(self.gen_blacklist('equilibrado')))
        low_grid.attach(self.entryBlacklistUSBIDs2, button_col2 - 1, row, scale_width, 1)

        row = row + 1
        # 8 ------------- EXCLUDE BLUETOOTH *
        # LABEL 8
        label44 = Gtk.Label(label=_('Exclude bluetooth devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)
        # BUTTON 8
        self.switchBlacklistBUSB2 = Gtk.Switch()
        self.switchBlacklistBUSB2.set_name('equilibrado')
        self.switchBlacklistBUSB2.set_halign(Gtk.Align.END)

        self.check_autostart_BlacklistBUSB(self.switchBlacklistBUSB2)

        low_grid.attach(self.switchBlacklistBUSB2, button_col2, row, 1, 1)

        row = row + 1

        # LABEL 9
        label44 = Gtk.Label(label=_('Exclude printer devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)
        # 9 ------------- EXCLUDE PRINTERS *
        # BUTTON 9
        self.switchBlacklistPrintUSB2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBlacklistPrintUSB2.set_name('equilibrado')
        self.check_autostart_BlacklistPrintUSB(self.switchBlacklistPrintUSB2)

        low_grid.attach(self.switchBlacklistPrintUSB2, button_col2, row, 1, 1)

        row = row + 1
        # 10 ------------ EXCLUDE NET DEVICES *
        # LABEL 10
        label44 = Gtk.Label(label=_('Exclude Ethernet devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 10
        self.switchBlacklistWWANUSB2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBlacklistWWANUSB2.set_name('equilibrado')

        self.check_autostart_BlacklistWWANUSB(self.switchBlacklistWWANUSB2)

        low_grid.attach(self.switchBlacklistWWANUSB2, button_col2, row, 1, 1)

        row = row + 1
        # 11 ------------ DISABLE USB AUTOSUSPENSION ON SHUTDOWN *
        # LABEL 11
        label44 = Gtk.Label(label=_('Disable USB autosuspend mode upon system shutdown:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 11
        self.switchShutdownSuspendUSB2 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchShutdownSuspendUSB2.set_name('equilibrado')

        self.check_autostart_ShutdownSuspendUSB(self.switchShutdownSuspendUSB2)

        low_grid.attach(self.switchShutdownSuspendUSB2, button_col2, row, 1, 1)
        # Connections
        self.switchUSBSuspend2.connect("notify::active", self.on_switchUSBSuspend_change, self.entryBlacklistUSBIDs2,
                                       self.switchBlacklistBUSB2, self.switchBlacklistPrintUSB2,
                                       self.switchBlacklistWWANUSB2, self.switchShutdownSuspendUSB2)
        self.on_switchUSBSuspend_change(self.switchUSBSuspend2, 'x', self.entryBlacklistUSBIDs2,
                                        self.switchBlacklistBUSB2, self.switchBlacklistPrintUSB2,
                                        self.switchBlacklistWWANUSB2, self.switchShutdownSuspendUSB2)


        # HIGH MODE PAGE **********************************************************
        print('\nLOADING HIGH MODE COMPONENTS ...')

        low_page_grid = Gtk.Grid(column_homogeneous=True,
                                 column_spacing=0,
                                 row_spacing=20)

        low_grid = Gtk.Grid(column_homogeneous=True,
                            row_homogeneous=False,
                            column_spacing=25,
                            row_spacing=20)

        low_page_grid.attach(low_grid, 0, 0, 2, 4)

        if self.min_resolution == True:
            scrolled_window1 = Gtk.ScrolledWindow()
            scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            
            scrolled_window1.set_min_content_height(400)
            scrolled_window1.set_min_content_width(1000)

            scrolled_window1.add_with_viewport(low_page_grid)
            notebook.append_page(scrolled_window1, Gtk.Label.new(_('Maximum Performance')))
        else:
            notebook.append_page(low_page_grid, Gtk.Label.new(_('Maximum Performance')))

        # ********* HIGH MODE COMPONENTS COLUMN 1 *********************************

        row = 1

        # LABEL 0
        label33 = Gtk.Label(label='')
        label33.set_markup(
            '<big><b>' + (_('Battery mode parameters (disabled when you connect AC power):')) + '</b></big>')
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, 6, 1)
        # 1 ------------- CPU LIMITER *
        # LABEL 1
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        table_icon.set_valign(Gtk.Align.END)
        low_grid.attach(table_icon, 0, row, label_width, 1)
        label33 = Gtk.Label(label=_('Limit CPU profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'warning.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this setting affects to performance'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 1
        store = Gtk.ListStore(int, str)
        store.append([1, (_('maximum'))])
        store.append([2, (_('medium'))])
        store.append([3, (_('none'))])
        self.comboBoxLimitCPU3 = Gtk.ComboBox.new_with_model_and_entry(store)
        self.comboBoxLimitCPU3.set_valign(Gtk.Align.CENTER)
        self.comboBoxLimitCPU3.set_halign(Gtk.Align.END)
        self.comboBoxLimitCPU3.set_entry_text_column(1)
        # self.comboBoxLimitCPU.set_active(self.check_autostart_comboBoxLimitCPU(self.comboBoxLimitCPU))

        value = config['SETTINGS']['limit_cpu_maximorendimiento']

        if value == '1':
            self.comboBoxLimitCPU3.set_active(0)
        elif value == '2':
            self.comboBoxLimitCPU3.set_active(1)
        elif value == '3':
            self.comboBoxLimitCPU3.set_active(2)

        low_grid.attach(self.comboBoxLimitCPU3, button_col - 1, row, scale_width, 1)
        # 2 ------------- CPU GOVERNOR *
        # LABEL 2
        governorCompatible, governor_name = governorIsCompatible()
        if governorCompatible:
            row = row + 1

            # LABEL 2
            label33 = Gtk.Label(label=_('CPU scaling governor saving profile:'))
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col, row, label_width, 1)

            # BUTTON 2
            store = Gtk.ListStore(int, str)
            if governor_name == 'intel_pstate':
                store.append([1, 'powersave'])
                store.append([2, 'performance'])
            elif governor_name == 'acpi-cpufreq':
                store.append([1, 'ondemand'])
                store.append([2, 'schedutil'])
                store.append([3, 'powersave'])
                store.append([4, 'performance'])
                store.append([5, 'conservative'])

            self.comboBoxGovernor3 = Gtk.ComboBox.new_with_model_and_entry(store)
            self.comboBoxGovernor3.set_name('maximorendimiento')
            self.comboBoxGovernor3.set_halign(Gtk.Align.END)
            self.comboBoxGovernor3.set_valign(Gtk.Align.CENTER)
            self.comboBoxGovernor3.set_entry_text_column(1)
            self.check_autostart_Governor(self.comboBoxGovernor3, governor_name)

            low_grid.attach(self.comboBoxGovernor3, button_col - 1, row, scale_width, 1)
        # 3 ------------- GRAPHICS SAVING *
        # LABEL 3
        row = row + 1
        # (3, 0)
        label33 = Gtk.Label(label=_('Graphic card saving profile (Nvidia-AMD-Intel):'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 3
        self.switchGraphics3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)

        self.switchGraphics3.set_sensitive(False)
        low_grid.attach(self.switchGraphics3, button_col, row, 1, 1)
        # 4 ------------- SOUND SAVING *
        # LABEL 3
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col, row, label_width, 1)
        label33 = Gtk.Label(label=_('Sound power saving profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this setting can cause slight clicks in sound output'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 3
        self.switchSound3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchSound3.set_name('maximorendimiento')

        self.check_autostart_switchSound(self.switchSound3)
        low_grid.attach(self.switchSound3, button_col, row, 1, 1)
        # 4 ------------- WIFI SAVING *
        # LABEL 4
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col, row, label_width, 1)
        label33 = Gtk.Label(label=_('Wi-Fi power saving profile:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: power save can cause an unstable wifi connection.'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 4
        self.switchWifiPower3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiPower3.set_name('maximorendimiento')

        self.check_autostart_switchWifiPower(self.switchWifiPower3)
        low_grid.attach(self.switchWifiPower3, button_col, row, 1, 1)
        # 6 ------------- DISABLE BLUETOOTH IF NOT IN USE *
        # LABEL 5
        row = row + 1
        label33 = Gtk.Label(label=_('Bluetooth disabled when not in use:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 5
        self.switchBluetoothNIU3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBluetoothNIU3.set_name('maximorendimiento')

        self.check_switchBluetooth(self.switchBluetoothNIU3)
        low_grid.attach(self.switchBluetoothNIU3, button_col, row, 1, 1)
        # 7 ------------- DISABLE WIFI IF NOT IN USE *
        # LABEL 6
        row = row + 1
        label33 = Gtk.Label(label=_('Wi-Fi disabled when not in use:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col, row, label_width, 1)

        # BUTTON 6
        self.switchWifiNIU3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiNIU3.set_name('maximorendimiento')

        self.switchWifiNIU3.set_valign(Gtk.Align.CENTER)
        self.check_autostart_switchWifiNIU(self.switchWifiNIU3)
        low_grid.attach(self.switchWifiNIU3, button_col, row, 1, 1)
        # 8 ------------- TDP ADJUST

        if tdpcontroller != '':
            row = row + 2
            label33 = Gtk.Label(label='')
            label33.set_markup('<big><b>' + (_('CPU TDP Settings')) + '</b></big>')
            if self.min_resolution == True:
                label33.set_name('title')
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col, row, 4, 1)

            if subprocess.getstatusoutput('which ' + tdpcontroller)[0] == 0:  # if TDP controller is installed
                # LABEL 7
                row = row + 1
                label33 = Gtk.Label(label=_('Synchronice battery mode with TDP mode:'))
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

                # BUTTON 7
                self.switchTDP3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                self.switchTDP3.set_name('power_tdpsync')

                self.check_autostart_switchTDP(self.switchTDP3)
                low_grid.attach(self.switchTDP3, button_col, row, 1, 1)

            else:
                print('TDP Controller not installed')
                # LABEL 7
                row = row + 1
                label33 = Gtk.Label(label=_('Synchronice battery mode with TDP mode:'))
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

                # BUTTON 7
                self.switchTDP3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                self.switchTDP3.set_name('power_tdpsync')
                self.switchTDP3.set_sensitive(False)
                # self.check_autostart_switchTDP(self.switchTDP)
                low_grid.attach(self.switchTDP3, button_col, row, 1, 1)

                # LABEL 7
                row = row + 1
                label33 = Gtk.Label()
                label33.set_markup("<a href='" + self.link + "'>" + _('Learn more about TDP Controller') + "</a>")
                label33.set_name('link')
                label33.set_halign(Gtk.Align.START)
                low_grid.attach(label33, label_col, row, label_width, 1)

        # ********* HIGH MODE COMPONENTS COLUMN 2 *********************************
        if not self.min_resolution == True:
            row = 1
        else:
            row = row+1

        label33 = Gtk.Label(label='')
        label33.set_markup('<big><b>' + (_('Persistent changes:')) + '</b></big>')
        if self.min_resolution == True:
            label33.set_name('title')
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, 5, 1)
        # 1 ------------- BRIGHTNESS *
        # LABEL 1
        row = row + 1
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        table_icon.set_valign(Gtk.Align.END)
        low_grid.attach(table_icon, label_col2, row, label_width2 - 1, 1)
        label33 = Gtk.Label(label=_('Set screen brightness:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(_('Note: this option reduces the battery consumption considerably'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 1

        self.scaleBrightness3 = Gtk.Scale()
        maxrendimientoBrightness = config['SETTINGS']['maxrendimiento_brightness']
        self.scaleBrightness3.set_adjustment(Gtk.Adjustment.new(int(maxrendimientoBrightness), 0, 100, 5, 5, 0))
        self.scaleBrightness3.set_digits(0)
        self.scaleBrightness3.set_hexpand(True)

        self.brightness_switch3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.END)
        self.brightness_switch3.set_name('power_brightness_switch')

        self.check_autostart_switchBrightness(self.brightness_switch3, self.scaleBrightness3)
        self.brightness_switch3.connect("state-set", self.brightness_switch_changed, self.scaleBrightness3)

        low_grid.attach(self.scaleBrightness3, button_col2 - 2, row, scale_width, 1)
        low_grid.attach(self.brightness_switch3, button_col2, row, 1, 1)

        if subprocess.getstatusoutput('echo $XDG_CURRENT_DESKTOP | grep -i gnome')[0] == 0:
            row = row + 1
            # LABEL 2
            label33 = Gtk.Label(label=_('Disable animations:'))
            label33.set_halign(Gtk.Align.START)
            low_grid.attach(label33, label_col2, row, label_width2, 1)
            # BUTTON 2
            self.switchAnimations3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
            self.switchAnimations3.set_name('maxrendimiento_animations')

            self.check_autostart_switchAnimations(self.switchAnimations3)
            low_grid.attach(self.switchAnimations3, button_col2, row, 1, 1)

        row = row + 1
        # 3 ------------- DISABLE BLUETOOTH ON STARTUP *
        # LABEL 3
        label33 = Gtk.Label(label=_("Bluetooth does not boot on start:"))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 3
        self.switchBluetoothOS3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBluetoothOS3.set_name('maximorendimiento')
        self.check_switchBluetoothOS(self.switchBluetoothOS3)
        low_grid.attach(self.switchBluetoothOS3, button_col2, row, 1, 1)
        # 4 ------------- DISABLE WIFI ON STARTUP *
        row = row + 1
        # LABEL 4
        label33 = Gtk.Label(label=_("Wi-Fi does not boot on start:"))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 4
        self.switchWifiOS3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiOS3.set_name('maximorendimiento')
        self.check_autostart_switchWifiOS(self.switchWifiOS3)
        low_grid.attach(self.switchWifiOS3, button_col2, row, 1, 1)
        # 5 ------------- DISABLE WIFI WHEN LAN *
        row = row + 1
        # LABEL 5
        label33 = Gtk.Label(label=_('Disable Wi-Fi when LAN is connected:'))
        label33.set_halign(Gtk.Align.START)
        low_grid.attach(label33, label_col2, row, label_width2, 1)
        # BUTTON 5
        self.switchWifiDisableLAN3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchWifiDisableLAN3.set_name('maximorendimiento')
        self.check_autostart_switchDisableLAN(self.switchWifiDisableLAN3)
        low_grid.attach(self.switchWifiDisableLAN3, button_col2, row, 1, 1)

        row = row + 1

        # 6 ------------- USB AUTOSUSPENSION
        # LABEL 6
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col2, row, label_width2, 1)
        label33 = Gtk.Label(label=_('Autosuspend USB Ports:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        icon.set_tooltip_text(
            _('Note: Set autosuspend mode for all USB devices upon system start or a change of power source. '
              'Input devices like mice and keyboards as well as scanners are excluded by default'))
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 6
        self.switchUSBSuspend3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchUSBSuspend3.set_name('maximorendimiento')
        self.check_autostart_USBSuspend(self.switchUSBSuspend3)
        low_grid.attach(self.switchUSBSuspend3, button_col2, row, 1, 1)

        row = row + 1
        # 7 ------------- AUTOSUSPENSION EXCLUDED IDS
        # LABEL 7
        table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
        low_grid.attach(table_icon, label_col2, row, label_width2, 1)
        label33 = Gtk.Label(label=_('Excluded USB IDs from USB autosuspend:'))
        label33.set_halign(Gtk.Align.START)
        table_icon.attach(label33, 0, 1, 0, 1,
                          xpadding=0,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)
        icon = Gtk.Image()
        icon_path = os.path.join(imagespath, 'help.png')
        icon.set_from_file(icon_path)
        # Se leen los diferentes USB que hay disponibles y se almacenan en un archivo temporalmente

        if os.system('lsusb | grep ID >> ' + user_home + '/.config/slimbookbattery/usbidlist') == 0:
            try:
                USBIDsList = ''
                # Se lee el archivo temporal que se ha creado y
                # se va sacando para que solo nos muestre el ID junto con el nombre del USB
                f = open(user_home + '/.config/slimbookbattery/usbidlist', 'r')
                line = f.readline()
                while line:
                    lineaActual = line
                    # Saca la posición del ID en la linea
                    IDPos = lineaActual.find("ID")
                    # Saca la última posición de la linea
                    longitud = len(lineaActual) - 1
                    # Una vez teniendo estas 2 posiciones ya tenemos el ID
                    # junto con el nombre del USB y se concatena al string USBIDsList
                    USBIDsList = USBIDsList + lineaActual[IDPos:longitud] + '\n'
                    line = f.readline()
                f.close()

                # Se elimina el archivo temporal
                os.system('rm ' + user_home + '/.config/slimbookbattery/usbidlist')
            except Exception:
                print('USB ID list 403')
        else:
            print('USB ID list 404')

        # En este tooltip
        icon.set_tooltip_text(
            _('Note: You need to write in the Text Box the USB IDs '
              '(separate with spaces) to exclude from autosuspend') + '.\n\n' + USBIDsList
        )
        icon.set_halign(Gtk.Align.START)
        table_icon.attach(icon, 1, 2, 0, 1,
                          xpadding=10,
                          ypadding=5,
                          xoptions=Gtk.AttachOptions.SHRINK,
                          yoptions=Gtk.AttachOptions.SHRINK)

        # BUTTON 7
        self.entryBlacklistUSBIDs3 = Gtk.Entry(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        if self.switchUSBSuspend3.get_active():
            self.entryBlacklistUSBIDs3.set_sensitive(True)
        else:
            self.entryBlacklistUSBIDs3.set_sensitive(False)
        self.entryBlacklistUSBIDs3.set_text(str(self.gen_blacklist('maximorendimiento')))

        low_grid.attach(self.entryBlacklistUSBIDs3, button_col2 - 1, row, scale_width, 1)

        row = row + 1
        # 8 ------------- EXCLUDE BLUETOOTH *
        # LABEL 8
        label44 = Gtk.Label(label=_('Exclude bluetooth devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)
        # BUTTON 8
        self.switchBlacklistBUSB3 = Gtk.Switch()
        self.switchBlacklistBUSB3.set_name('maximorendimiento')
        self.switchBlacklistBUSB3.set_halign(Gtk.Align.END)

        self.check_autostart_BlacklistBUSB(self.switchBlacklistBUSB3)

        low_grid.attach(self.switchBlacklistBUSB3, button_col2, row, 1, 1)

        row = row + 1
        # 9 ------------- EXCLUDE PRINTERS *
        # LABEL 9
        label44 = Gtk.Label(label=_('Exclude printer devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 9
        self.switchBlacklistPrintUSB3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBlacklistPrintUSB3.set_name('maximorendimiento')

        self.check_autostart_BlacklistPrintUSB(self.switchBlacklistPrintUSB3)

        low_grid.attach(self.switchBlacklistPrintUSB3, button_col2, row, 1, 1)

        row = row + 1
        # 10 ------------ EXCLUDE NET DEVICES *
        # LABEL 10
        label44 = Gtk.Label(label=_('Exclude Ethernet devices from USB autosuspend:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 10
        self.switchBlacklistWWANUSB3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchBlacklistWWANUSB3.set_name('maximorendimiento')
        self.check_autostart_BlacklistWWANUSB(self.switchBlacklistWWANUSB3)

        low_grid.attach(self.switchBlacklistWWANUSB3, button_col2, row, 1, 1)

        row = row + 1
        # 11 ------------ DISABLE USB AUTOSUSPENSION ON SHUTDOWN *
        # LABEL 11
        label44 = Gtk.Label(label=_('Disable USB autosuspend mode upon system shutdown:'))
        label44.set_halign(Gtk.Align.START)
        low_grid.attach(label44, label_col2, row, label_width2, 1)

        # BUTTON 11
        self.switchShutdownSuspendUSB3 = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
        self.switchShutdownSuspendUSB3.set_name('maximorendimiento')
        self.check_autostart_ShutdownSuspendUSB(self.switchShutdownSuspendUSB3)
        low_grid.attach(self.switchShutdownSuspendUSB3, button_col2, row, 1, 1)
        # Connections
        self.switchUSBSuspend3.connect("notify::active", self.on_switchUSBSuspend_change, self.entryBlacklistUSBIDs3,
                                       self.switchBlacklistBUSB3, self.switchBlacklistPrintUSB3,
                                       self.switchBlacklistWWANUSB3, self.switchShutdownSuspendUSB3)
        self.on_switchUSBSuspend_change(self.switchUSBSuspend3, 'x', self.entryBlacklistUSBIDs3,
                                        self.switchBlacklistBUSB3, self.switchBlacklistPrintUSB3,
                                        self.switchBlacklistWWANUSB3, self.switchShutdownSuspendUSB3)

        # CYCLES PAGE ************************************************************

        cycles_page_grid = Gtk.Grid(column_homogeneous=True,
                                    column_spacing=0,
                                    row_spacing=20)

        cycles_grid = Gtk.Grid(column_homogeneous=True,
                               column_spacing=40,
                               row_spacing=20)
        cycles_grid.set_halign(Gtk.Align.CENTER)

        cycles_page_grid.attach(cycles_grid, 0, 3, 2, 1)

        if self.min_resolution == True:
            scrolled_window1 = Gtk.ScrolledWindow()
            scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            
            scrolled_window1.set_min_content_height(400)
            scrolled_window1.set_min_content_width(1000)

            scrolled_window1.add_with_viewport(cycles_page_grid)
            notebook.append_page(scrolled_window1, Gtk.Label.new(_('Cycles')))
        else:
            notebook.append_page(cycles_page_grid, Gtk.Label.new(_('Cycles')))

        # ********* CYCLES COMPONENTS ********************************************
        # (0, 0)
        label22 = Gtk.Label(label=_('Enable cycle alerts'))
        label22.set_halign(Gtk.Align.START)
        cycles_grid.attach(label22, 0, 0, 1, 1)

        # (0, 1)
        self.switchAlerts = Gtk.Switch()
        self.switchAlerts.set_halign(Gtk.Align.START)

        if config['CONFIGURATION']['alerts'] == '1':
            self.switchAlerts.set_active(True)

        # self.switchAlerts.set_active(self.check_autostart_switchAlerts(self.switchAlerts))
        cycles_grid.attach(self.switchAlerts, 1, 0, 1, 1)

        # (1, 0)
        label22 = Gtk.Label(label=_('Max battery value:'))
        label22.set_halign(Gtk.Align.START)
        cycles_grid.attach(label22, 0, 1, 1, 1)

        # (1, 1)
        self.scaleMaxBatVal = Gtk.Scale()
        self.scaleMaxBatVal.set_size_request(200, 10)
        max_value = config['CONFIGURATION']['max_battery_value']
        self.scaleMaxBatVal.set_adjustment(Gtk.Adjustment.new(int(max_value), 0, 100, 5, 5, 0))
        self.scaleMaxBatVal.set_digits(0)
        self.scaleMaxBatVal.set_hexpand(True)
        cycles_grid.attach(self.scaleMaxBatVal, 1, 1, 1, 1)

        # (2, 0)
        label22 = Gtk.Label(label=_('Min battery value:'))
        label22.set_halign(Gtk.Align.START)
        cycles_grid.attach(label22, 0, 2, 1, 1)

        # (2, 1)
        self.scaleMinBatVal = Gtk.Scale()
        self.scaleMinBatVal.set_size_request(200, 10)
        min_value = config['CONFIGURATION']['min_battery_value']
        self.scaleMinBatVal.set_adjustment(Gtk.Adjustment.new(int(min_value), 0, 100, 5, 5, 0))
        self.scaleMinBatVal.set_digits(0)
        self.scaleMinBatVal.set_hexpand(True)
        cycles_grid.attach(self.scaleMinBatVal, 1, 2, 1, 1)

        # (3, 0)
        label22 = Gtk.Label(label=_('Number of times:'))
        label22.set_halign(Gtk.Align.START)
        cycles_grid.attach(label22, 0, 3, 1, 1)

        # (3, 1)
        self.scaleNumTimes = Gtk.Scale()
        self.scaleNumTimes.set_size_request(200, 10)
        max_value = 15
        max_value = config['CONFIGURATION']['max_battery_times']
        self.scaleNumTimes.set_adjustment(Gtk.Adjustment.new(int(max_value), 0, 10, 5, 5, 0))
        self.scaleNumTimes.set_digits(0)
        self.scaleNumTimes.set_hexpand(True)
        cycles_grid.attach(self.scaleNumTimes, 1, 3, 1, 1)

        # (4, 0)
        label22 = Gtk.Label(label=_('Time between Warnings:'))
        label22.set_halign(Gtk.Align.START)
        cycles_grid.attach(label22, 0, 4, 1, 1)

        # (4, 1)
        self.scaleTimeWarnings = Gtk.Scale()
        self.scaleTimeWarnings.set_size_request(200, 10)
        min_value = config['CONFIGURATION']['time_between_warnings']
        self.scaleTimeWarnings.set_adjustment(Gtk.Adjustment.new(int(min_value), 0, 300, 5, 5, 0))
        self.scaleTimeWarnings.set_digits(0)
        self.scaleTimeWarnings.set_hexpand(True)
        cycles_grid.attach(self.scaleTimeWarnings, 1, 4, 1, 1)

        # BATTERY INFO PAGE ******************************************************

        cycles_page_grid = Gtk.Grid(column_homogeneous=True,
                                    column_spacing=0,
                                    row_spacing=20)

        battery_grid = Gtk.Grid(column_homogeneous=True,
                                column_spacing=0,
                                row_spacing=20)
        battery_grid.set_halign(Gtk.Align.CENTER)

        cycles_page_grid.attach(battery_grid, 0, 2, 2, 1)

        if self.min_resolution == True:
            scrolled_window1 = Gtk.ScrolledWindow()
            scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            
            scrolled_window1.set_min_content_height(400)
            scrolled_window1.set_min_content_width(1000)

            scrolled_window1.add_with_viewport(cycles_page_grid)
            notebook.append_page(scrolled_window1, Gtk.Label.new(_('Battery')))
        else:
            notebook.append_page(cycles_page_grid, Gtk.Label.new(_('Battery')))

        # ********* BATTERY COMPONENTS *******************************************

        # GET DATA
        data = self.read_bat()

        col1 = 1

        col2 = 3

        lb_bat = Gtk.Label(label='')
        lb_bat.set_markup('<b>' + (_('Battery')) + '</b>')
        lb_bat.set_halign(Gtk.Align.START)
        battery_grid.attach(lb_bat, col1, 1, 2, 1)

        # (0, 2)
        bat = Gtk.Label(label=data[0])
        bat.set_halign(Gtk.Align.START)
        battery_grid.attach(bat, col2, 1, 2, 1)

        # (1, 1)
        lbl_man = Gtk.Label(label='')
        lbl_man.set_markup('<b>' + (_('Manufacturer:')) + '</b>')
        lbl_man.set_halign(Gtk.Align.START)
        battery_grid.attach(lbl_man, col1, 2, 2, 1)

        # (1, 2)
        man = Gtk.Label(label=data[1])
        man.set_halign(Gtk.Align.START)
        battery_grid.attach(man, col2, 2, 2, 1)

        # (2, 1)
        lbl_model = Gtk.Label(label='')
        lbl_model.set_markup('<b>' + (_('Battery model:')) + '</b>')
        lbl_model.set_halign(Gtk.Align.START)
        battery_grid.attach(lbl_model, col1, 3, 2, 1)

        # (2, 2)
        model = Gtk.Label(label=data[2])
        model.set_halign(Gtk.Align.START)
        battery_grid.attach(model, col2, 3, 2, 1)

        # (3, 1)
        lbl_tech = Gtk.Label(label='')
        lbl_tech.set_markup('<b>' + (_('Technology:')) + '</b>')
        lbl_tech.set_halign(Gtk.Align.START)
        battery_grid.attach(lbl_tech, col1, 4, 2, 1)

        # (3, 2)
        label66 = Gtk.Label(label=data[3])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 4, 2, 1)

        # (4, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Remaining battery:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 5, 2, 1)

        # (4, 2)
        label66 = Gtk.Label(label=data[4])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 5, 2, 1)

        # (5, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Maximum capacity:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 6, 2, 1)

        # (5, 2)
        label66 = Gtk.Label(label=data[5])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 6, 2, 1)

        # (6, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Status:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 7, 2, 1)

        # (6, 2)
        label66 = Gtk.Label(label=data[6])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 7, 2, 1)

        # (7, 1)
        if data[6].lower() == 'charging':
            label66 = Gtk.Label(label='')
            label66.set_markup('<b>' + (_('Time to full:')) + '</b>')
            label66.set_halign(Gtk.Align.START)
            battery_grid.attach(label66, col1, 8, 2, 1)

        elif data[6].lower() == 'discharging':
            label66 = Gtk.Label(label='')
            label66.set_markup('<b>' + (_('Time to empty:')) + '</b>')
            label66.set_halign(Gtk.Align.START)
            battery_grid.attach(label66, col1, 8, 2, 1)

        elif data[6].lower() == 'fully-charged':
            label66 = Gtk.Label(label='')
            label66.set_markup('<b>' + (_('Time to full:')) + '</b>')
            label66.set_halign(Gtk.Align.START)
            battery_grid.attach(label66, col1, 8, 2, 1)

        else:
            label66 = Gtk.Label(label='')
            label66.set_markup('<b>' + (_('Time to full-empty charge:')) + '</b>')
            label66.set_halign(Gtk.Align.START)
            battery_grid.attach(label66, col1, 8, 2, 1)

        # (7, 2)
        label66 = Gtk.Label(label=data[7])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 8, 2, 1)

        # (8, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Rechargeable:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 9, 2, 1)

        # (8, 2)
        label66 = Gtk.Label(label=data[8])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 9, 2, 1)

        # (9, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Power supply:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 10, 2, 1)

        # (9, 2)
        label66 = Gtk.Label(label=data[9])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 10, 2, 1)

        # (10, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Energy full:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 11, 2, 1)

        # (10, 2)
        label66 = Gtk.Label(label=data[10])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 11, 2, 1)

        # (11, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Energy full design:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 12, 2, 1)

        # (11, 2)
        label66 = Gtk.Label(label=data[11])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 12, 2, 1)

        # (12, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Energy rate:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 13, 2, 1)

        # (12, 2)
        label66 = Gtk.Label(label=data[12])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 13, 2, 1)

        # (13, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Voltage:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 14, 2, 1)

        # (13, 2)
        label66 = Gtk.Label(label=data[13])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 14, 2, 1)

        # (14, 1)
        label66 = Gtk.Label(label='')
        label66.set_markup('<b>' + (_('Last update of the battery information:')) + '</b>')
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col1, 15, 2, 1)

        # (14, 2)
        label66 = Gtk.Label(label=data[14])
        label66.set_halign(Gtk.Align.START)
        battery_grid.attach(label66, col2, 15, 2, 1)

        # INFO PAGE **************************************************************

        info_page_grid = Gtk.Grid(column_homogeneous=True,
                                  column_spacing=0,
                                  row_spacing=20)
        


        info_grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=0,
                             row_spacing=15)
        if self.min_resolution == True:
            info_grid.set_name('smaller_label')


        info_page_grid.attach(info_grid, 0, 0, 2, 4)
        


        if self.min_resolution == True:
            scrolled_window1 = Gtk.ScrolledWindow()
            scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            
            scrolled_window1.set_min_content_height(400)
            scrolled_window1.set_min_content_width(1000)

            scrolled_window1.add_with_viewport(info_page_grid)
            notebook.append_page(scrolled_window1, Gtk.Label.new(_('Information')))
        else:
            notebook.append_page(info_page_grid, Gtk.Label.new(_('Information')))

        # ********* APPLICATION INFO COMPONENTS ***********************************

        hbox = Gtk.HBox(spacing=15)
        hbox.set_halign(Gtk.Align.CENTER)
        # Icon
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'normal.png'),
            width=60,
            height=60,
            preserve_aspect_ratio=True)
        iconApp = Gtk.Image.new_from_pixbuf(pixbuf)

        # Title
        label77 = Gtk.Label(label='')
        label77.set_markup('<span font="20"><b>Slimbook Battery 4</b></span>')
        label77.set_justify(Gtk.Justification.CENTER)

        hbox.add(label77)
        hbox.add(iconApp)

        info_grid.attach(hbox, 0, 1, 5, 1)

        # Text 1
        label77 = Gtk.Label(label='')
        msg = "<span>{}\n{}</span>".format(
            _("Slimbook Battery is a battery optimization application for "
              "portable devices and can increase the battery"),
            _("life up to 50%. For this purpose, the third-party software is "
              "used to manage and configure the system resources.")
        )
        label77.set_markup(msg)
        label77.set_justify(Gtk.Justification.CENTER)
        info_grid.attach(label77, 0, 2, 5, 1)

        # (3, 0)
        label77 = Gtk.Label(label='')
        label77.set_markup("<span>" + (
            _("Special thanks to TLP (© 2019, linrunner), Nvidia, AMD and Intel "
              "for offering us the necessary tools to make it possible!")) + "</span>")
        label77.set_justify(Gtk.Justification.CENTER)
        info_grid.attach(label77, 0, 3, 5, 1)

        # (4, 0)
        label77 = Gtk.Label(label='')
        label77.set_markup("<span>" + (
            _("If this application has been useful to you, "
              "consider saying it in our social networks or even buy a SLIMBOOK ;)")) + "</span>")
        label77.set_justify(Gtk.Justification.CENTER)
        info_grid.attach(label77, 0, 4, 5, 1)

        # (5, 0)
        hbox = Gtk.HBox(spacing=5)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'twitter.png'),
            width=25,
            height=25,
            preserve_aspect_ratio=True)

        twitter = Gtk.Image.new_from_pixbuf(pixbuf)

        hbox.pack_start(twitter, False, False, 0)

        label77 = Gtk.Label(label=' ')
        label77.set_markup("<span><b><a href='https://twitter.com/SlimbookEs'>@SlimbookEs</a></b>    </span>")
        label77.set_justify(Gtk.Justification.CENTER)
        hbox.pack_start(label77, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'facebook.png'),
            width=25,
            height=25,
            preserve_aspect_ratio=True)

        facebook = Gtk.Image.new_from_pixbuf(pixbuf)
        hbox.pack_start(facebook, False, False, 0)

        label77 = Gtk.Label(label=' ')
        label77.set_markup("<span><b><a href='https://www.facebook.com/slimbook.es'>Slimbook</a></b>    </span>")
        label77.set_justify(Gtk.Justification.CENTER)
        hbox.pack_start(label77, False, False, 0)

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(imagespath, 'insta.png'),
                width=25,
                height=25,
                preserve_aspect_ratio=True)
        except Exception:
            print()

        instagram = Gtk.Image.new_from_pixbuf(pixbuf)
        hbox.pack_start(instagram, False, False, 0)
        label77 = Gtk.Label(label=' ')
        label77.set_markup("<span><b><a href='https://www.instagram.com/slimbookes/?hl=en'>@slimbookes</a></b></span>")
        label77.set_justify(Gtk.Justification.CENTER)
        hbox.pack_start(label77, False, False, 0)
        hbox.set_halign(Gtk.Align.CENTER)
        info_grid.attach(hbox, 0, 6, 5, 1)

        # (6, 0)
        label77 = Gtk.Label(label='')
        msg = "<span><b>{}</b>{}\n{}</span>".format(
            _("IMPORTANT NOTE:"),
            _(" If you have any software, widget or application that changes the CPU profile, battery"),
            _("optimization or similar, it may affect the operation of this application. "
              "Use it under your responsibility.")
        )
        label77.set_markup(msg)
        label77.set_justify(Gtk.Justification.CENTER)
        info_grid.attach(label77, 0, 7, 5, 1)

        hbox = Gtk.HBox()
        hbox.set_halign(Gtk.Align.CENTER)
        # (8, 0)
        label77 = Gtk.LinkButton(uri='https://slimbook.es/', label=(_('Visit SLIMBOOK website')))
        label77.set_name('link')
        label77.set_halign(Gtk.Align.CENTER)
        hbox.add(label77)
        # info_grid.attach(label77, 0, 9, 5, 1)

        # (9, 0)
        label77 = Gtk.LinkButton(uri=(_('strurlwebsite')), label=(_('Tutorial to learn to use Slimbook Battery')))
        label77.set_name('link')
        label77.set_halign(Gtk.Align.CENTER)
        hbox.add(label77)

        label77 = Gtk.LinkButton(uri="https://github.com/slimbook/slimbookbattery/tree/main/src/locale",
                                 label=(_('Help us with translations!')))
        label77.set_name('link')
        label77.set_halign(Gtk.Align.CENTER)
        hbox.add(label77)

        info_grid.attach(hbox, 0, 10, 5, 1)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'GitHub_Logo_White.png'),
            width=150,
            height=30,
            preserve_aspect_ratio=True)

        img = Gtk.Image()
        img.set_from_pixbuf(pixbuf)

        github = Gtk.LinkButton(uri="https://github.com/slimbook/slimbookbattery")
        github.set_name('link')
        github.set_halign(Gtk.Align.CENTER)
        github.set_image(img)

        hbox = Gtk.HBox()
        hbox.set_halign(Gtk.Align.CENTER)

        hbox.add(github)

        info_grid.attach(hbox, 0, 11, 5, 1)

        label77 = Gtk.Label()
        msg = "<span>{}<a href='https://www.patreon.com/slimbook'>Patreon</a>{}</span>".format(
            _("If you want you can support the developement of this app "
              "and several more to come by joining us on "),
            _(" or buying a brand new Slimbook ;)")
        )
        label77.set_markup(msg)
        label77.set_justify(Gtk.Justification.CENTER)
        info_grid.attach(label77, 0, 12, 5, 1)

        # (10, 0)
        label77 = Gtk.Label(label='')
        msg = "<span><b>{}</b> {} {}</span>".format(
            _("Info:"),
            _("Contact with us if you find something wrong. "
              "We would appreciate that you attach the file that is generated"),
            _("by clicking the button below")
        )
        label77.set_markup(msg)
        label77.set_justify(Gtk.Justification.CENTER)
        info_grid.attach(label77, 0, 13, 5, 1)

        label77 = Gtk.Label(label=' ')
        label77.set_markup("<span><b>" + (_("Send an e-mail to: ")) + "dev@slimbook.es</b></span>")
        label77.set_justify(Gtk.Justification.CENTER)

        
        # (12, 0)
        self.buttonReportFile = Gtk.Button(label=(_('Generate report file')))
        self.buttonReportFile.connect("clicked", self.on_buttonReportFile_clicked)
        self.buttonReportFile.set_halign(Gtk.Align.CENTER)
 

        hbox = Gtk.HBox()
        hbox.add(label77)
        hbox.pack_start( self.buttonReportFile, True, True, 0)
        info_grid.attach(hbox, 1, 15, 3, 1)

        # (13, 0)
        label77 = Gtk.Label(label='')
        label77.set_markup(_('The software is provided  as is , without warranty of any kind.'))
        label77.set_justify(Gtk.Justification.CENTER)
        info_grid.attach(label77, 0, 16, 5, 1)

        
        # (14, 0)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(imagespath, 'cc.png'),
            width=100,
            height=200,
            preserve_aspect_ratio=True)
        Gtk.Image.new_from_pixbuf(pixbuf)

        # END
        self.child_process.terminate()
        # SHOW
        self.show_all()

    # CLASS FUNCTIONS ***********************************
    def brightness_switch_changed(self, switchBrightness, state, scale):
        if state:
            scale.set_sensitive(True)
        else:
            scale.set_sensitive(False)

    def check_autostart_switchTDP(self, switchTDP):
        # print('TDP')
        tdp_adjustment = switchTDP.get_name()
        stat = config['TDP'][tdp_adjustment]
        if stat == '1':
            switchTDP.set_active(True)

        elif stat == '0':
            switchTDP.set_active(False)

    def check_autostart_switchBrightness(self, switchBrightness, scale):
        mode_brightness = switchBrightness.get_name()
        try:
            stat = config['SETTINGS'][mode_brightness]
        except (ValueError, IndexError, KeyError):
            import check_config

        stat = config['SETTINGS'][mode_brightness]
        if stat == '1':
            switchBrightness.set_active(True)
            scale.set_sensitive(True)
        elif stat == '0':
            switchBrightness.set_active(False)
            scale.set_sensitive(False)

    def check_autostart_switchAnimations(self, switchAnimations):
        mode_anims = switchAnimations.get_name()
        stat = config['SETTINGS'][mode_anims]
        if stat == '1':
            switchAnimations.set_active(True)
        elif stat == '0':
            switchAnimations.set_active(False)

    def check_autostart_USBSuspend(self, switchUSBSuspend):
        mode = switchUSBSuspend.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_AUTOSUSPEND=0'")[0] == 0:
            switchUSBSuspend.set_active(False)
            # print('Disabling autosuspend switch')
        elif subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_AUTOSUSPEND=1'")[0] == 0:
            switchUSBSuspend.set_active(True)

    def check_autostart_switchDisableLAN(self, switchWifiDisableLAN):  # All modes
        mode = switchWifiDisableLAN.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)

        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'DEVICES_TO_DISABLE_ON_LAN_CONNECT' | grep 'wifi'")[0] == 0 \
            and subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'DEVICES_TO_ENABLE_ON_LAN_DISCONNECT' | grep 'wifi'")[0] == 0:
            switchWifiDisableLAN.set_active(True)
        else:
            switchWifiDisableLAN.set_active(False)

    def check_autostart_ShutdownSuspendUSB(self, switchShutdownSuspendUSB):
        mode = switchShutdownSuspendUSB.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=0'")[0] == 0:
            switchShutdownSuspendUSB.set_active(False)
        elif subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=1'")[0] == 0:
            switchShutdownSuspendUSB.set_active(True)

    def check_autostart_BlacklistWWANUSB(self, switchBlacklistWWANUSB):
        mode = switchBlacklistWWANUSB.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_BLACKLIST_WWAN=0'")[0] == 0:
            switchBlacklistWWANUSB.set_active(False)
        elif subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_BLACKLIST_WWAN=1'")[0] == 0:
            switchBlacklistWWANUSB.set_active(True)

    def check_autostart_BlacklistBUSB(self, switchBlacklistBUSB):
        mode = switchBlacklistBUSB.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_BLACKLIST_BTUSB=0'")[0] == 0:
            switchBlacklistBUSB.set_active(False)
        elif subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_BLACKLIST_BTUSB=1'")[0] == 0:
            switchBlacklistBUSB.set_active(True)

    def check_autostart_BlacklistPrintUSB(self, switchBlacklistPrintUSB):
        mode = switchBlacklistPrintUSB.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_BLACKLIST_PRINTER=0'")[0] == 0:
            switchBlacklistPrintUSB.set_active(False)
        elif subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'USB_BLACKLIST_PRINTER=1'")[0] == 0:
            switchBlacklistPrintUSB.set_active(True)

    def check_autostart_switchWifiOS(self, switchWifiOS):  # All modes
        mode = switchWifiOS.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'DEVICES_TO_DISABLE_ON_STARTUP' | grep 'wifi'")[0] == 0:
            switchWifiOS.set_active(True)
        else:
            switchWifiOS.set_active(False)
            # print('Wifi STARTUP not found')

    def check_autostart_switchWifiNIU(self, switchWifiNIU):  # All modes
        mode = switchWifiNIU.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE' | grep 'wifi'")[0] == 0:
            switchWifiNIU.set_active(True)
        else:
            switchWifiNIU.set_active(False)

    def check_autostart_switchWifiPower(self, switchWifiPower):  # All modes
        mode = switchWifiPower.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'WIFI_PWR_ON_BAT=on'")[0] == 0:
            switchWifiPower.set_active(True)
        else:
            switchWifiPower.set_active(False)

    def check_autostart_switchSound(self, switchSound):  # All modes
        mode = switchSound.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'SOUND_POWER_SAVE_ON_BAT=1'")[0] == 0:
            switchSound.set_active(True)
        else:
            switchSound.set_active(False)

    def check_autostart_Graphics(self, switchGraphics):  # Only in saving and balanced mode
        mode = switchGraphics.get_name()
        if mode == 'ahorrodeenergia':
            graphics = config['SETTINGS']['graphics_ahorro']
        elif mode == 'equilibrado':
            graphics = config['SETTINGS']['graphics_equilibrado']

        if graphics == '0':
            # print('Graphics saving:  Off')
            switchGraphics.set_active(False)
        elif graphics == '1':
            # print('Graphics saving:  On')
            switchGraphics.set_active(True)

    def check_autostart_Governor(self, comboBoxGovernor, governor_name):  # All modes
        mode = comboBoxGovernor.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if governor_name == 'intel_pstate':
            if subprocess.getstatusoutput(
                    "cat " + file_mode + " | grep 'CPU_SCALING_GOVERNOR_ON_BAT=powersave'")[0] == 0:
                comboBoxGovernor.set_active(0)
            elif subprocess.getstatusoutput(
                    "cat " + file_mode + " | grep 'CPU_SCALING_GOVERNOR_ON_BAT=performance'")[0] == 0:
                comboBoxGovernor.set_active(1)
            else:
                print('Setting default mode powersave')
                comboBoxGovernor.set_active(0)
        elif governor_name == 'acpi-cpufreq':
            if subprocess.getstatusoutput(
                    "cat " + file_mode + " | grep 'CPU_SCALING_GOVERNOR_ON_BAT=ondemand'")[0] == 0:
                comboBoxGovernor.set_active(0)
            elif subprocess.getstatusoutput(
                    "cat " + file_mode + " | grep 'CPU_SCALING_GOVERNOR_ON_BAT=schedutil'")[0] == 0:
                comboBoxGovernor.set_active(1)
            elif subprocess.getstatusoutput(
                    "cat " + file_mode + " | grep 'CPU_SCALING_GOVERNOR_ON_BAT=powersave'")[0] == 0:
                comboBoxGovernor.set_active(2)
            elif subprocess.getstatusoutput(
                    "cat " + file_mode + " | grep 'CPU_SCALING_GOVERNOR_ON_BAT=performance'")[0] == 0:
                comboBoxGovernor.set_active(3)
            elif subprocess.getstatusoutput(
                    "cat " + file_mode + " | grep 'CPU_SCALING_GOVERNOR_ON_BAT=conservative'")[0] == 0:
                comboBoxGovernor.set_active(4)
            else:
                print('Setting default mode on-demand')
                comboBoxGovernor.set_active(0)

    def check_switchBluetooth(self, switch):  # All modes
        mode = switch.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE' | grep 'bluetooth'")[0] == 0:
            switch.set_active(True)
        else:
            switch.set_active(False)

    def check_switchBluetoothOS(self, switch):  # All modes
        mode = switch.get_name()
        file_mode = os.path.join(user_home, '.config/slimbookbattery/custom', mode)
        if subprocess.getstatusoutput(
                "cat " + file_mode + " | grep 'DEVICES_TO_DISABLE_ON_STARTUP' | grep 'bluetooth'")[0] == 0:
            switch.set_active(True)
        else:
            switch.set_active(False)

    def gen_blacklist(self, mode):
        USBBlacklist = subprocess.getoutput(
            'cat ' + user_home + '/.config/slimbookbattery/custom/' + mode + ' | grep USB_BLACKLIST=')
        pos1 = USBBlacklist.find('\"') + 1
        pos2 = len(USBBlacklist) - 1
        USBBlacklist = USBBlacklist[pos1:pos2]
        return USBBlacklist

    def on_switchUSBSuspend_change(self, switchUSBSuspend, gparam, switch1, switch2, switch3, switch4,
                                   switch5):  # All modes
        mode = switchUSBSuspend.get_name()
        if switchUSBSuspend.get_active():
            # Enables USB switches
            mode = switchUSBSuspend.get_name()

            self.gen_blacklist(mode)

            switch1.set_sensitive(True)

            switch2.set_sensitive(True)

            switch3.set_sensitive(True)

            switch4.set_sensitive(True)

            switch5.set_sensitive(True)
        else:
            # Deactivates all device USB switches
            switch1.set_sensitive(False)
            switch1.set_sensitive(False)
            switch2.set_sensitive(False)
            switch3.set_sensitive(False)
            switch4.set_sensitive(False)
            switch5.set_sensitive(False)

    def read_bat(self):
        var = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep native-path")
        if cmd[0] == 0:
            batDevice = cmd[1]
            batDevice = batDevice.split()
            batDevice = batDevice[1]
        else:
            batDevice = (_('Unknown'))
        var[0] = batDevice

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep vendor")
        if cmd[0] == 0:
            manufacturer = cmd[1]
            manufacturer = manufacturer.split()
            manufacturer = manufacturer[1]
        else:
            manufacturer = (_('Unknown'))
        var[1] = manufacturer

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep model")
        if cmd[0] == 0:
            model = cmd[1]
            model = model.split()
            model = model[1]
        else:
            model = (_('Unknown'))
        var[2] = model

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep technology")
        if cmd[0] == 0:
            technology = cmd[1]
            technology = technology.split()
            technology = technology[1]
        else:
            technology = (_('Unknown'))
        var[3] = technology.capitalize()

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep percentage")
        if cmd[0] == 0:
            currentCharge = cmd[1]
            currentCharge = currentCharge.split()
            currentCharge = currentCharge[1]
        else:
            currentCharge = (_('Unknown'))
        var[4] = currentCharge

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep capacity")
        if cmd[0] == 0:
            maxCapacity = cmd[1]
            maxCapacity = maxCapacity.split()
            maxCapacity = maxCapacity[1]
        else:
            maxCapacity = (_('Unknown'))
        var[5] = maxCapacity

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep state")
        if cmd[0] == 0:
            status = cmd[1]
            status = status.split()
            status = status[1]
        else:
            status = (_('Unknown'))
        var[6] = status.capitalize()

        if status == 'discharging':
            cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep 'time to empty'")
            if cmd[0] == 0:
                timeTo = cmd[1]
                timeTo = timeTo.split()
                #print(timeTo)
                if timeTo[4] == 'hours':
                    timeTo = timeTo[3] + (_(' hours'))
                else:
                    timeTo = timeTo[3] + (_(' min'))
            else:
                timeTo = (_('Unknown'))
        elif status == 'charging':
            cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep 'time to full'")
            if cmd[0] == 0:
                timeTo = cmd[1]
                timeTo = timeTo.split()
                if timeTo[4] == 'hours':
                    timeTo = timeTo[3] + (_(' hours'))
                else:
                    timeTo = timeTo[3] + (_(' min'))
            else:
                timeTo = (_('Unknown'))
        elif status == 'fully-charged':
            timeTo = (_('Fully charged'))
        else:
            timeTo = (_('Unknown'))
        var[7] = timeTo

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep rechargeable")
        if cmd[0] == 0:
            rechargeable = cmd[1]
            rechargeable = rechargeable.split()
            rechargeable = rechargeable[1]
        else:
            rechargeable = (_('Unknown'))
        var[8] = rechargeable.capitalize()

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep 'power supply'")
        if cmd[0] == 0:
            powerSupply = cmd[1]
            powerSupply = powerSupply.split()
            powerSupply = powerSupply[2]
        else:
            powerSupply = (_('Unknown'))
        var[9] = powerSupply.capitalize()

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep energy-full")
        if cmd[0] == 0:
            chargeFull = cmd[1]
            chargeFull = chargeFull.split()
            chargeFull = str(chargeFull[1]) + ' Wh'
        else:
            chargeFull = (_('Unknown'))
        var[10] = chargeFull

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep energy-full-design")
        if cmd[0] == 0:
            chargeDesign = cmd[1]
            chargeDesign = chargeDesign.split()
            chargeDesign = str(chargeDesign[1]) + ' Wh'
        else:
            chargeDesign = (_('Unknown'))
        var[11] = chargeDesign

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep energy-rate")
        if cmd[0] == 0:
            chargeRate = subprocess.getoutput("upower -i `upower -e | grep 'BAT'` | grep energy-rate")
            chargeRate = chargeRate.split()
            chargeRate = str(chargeRate[1]) + ' Wh'
        else:
            chargeRate = (_('Unknown'))
        var[12] = chargeRate

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep voltage")
        if cmd[0] == 0:
            voltage = cmd[1]
            voltage = voltage.split()
            voltage = str(voltage[1]) + ' V'
        else:
            voltage = (_('Unknown'))
        var[13] = voltage

        cmd = subprocess.getstatusoutput("upower -i `upower -e | grep 'BAT'` | grep updated")
        if cmd[0] == 0:
            infoUpdated = cmd[1]
            infoUpdated = infoUpdated.split()
            date = ''
            for i in range(len(infoUpdated)):
                if int(i) != 0:
                    date = str(date) + str(infoUpdated[i]) + ' '
            infoUpdated = date
        else:
            infoUpdated = (_('Unknown'))
        var[14] = infoUpdated.capitalize()

        return var

    def on_button_toggled(self, button, name):  # Saves actual mode in a variable
        self.modo_actual = name

    def on_buttonRestGeneral_clicked(self, buttonRestGeneral):
        print('Reset values called')
        os.system('pkexec slimbookbattery-pkexec restore')
        self.hide()

        win = Preferences()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()

    def on_switch_activated(self, switch):  # Returns switch state

        if switch.get_active():
            state = True
            return state
        else:
            state = False
            return state

    def messagedialog(self, title, message):

        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK)

        dialog.set_markup("<b>%s</b>" % title)
        dialog.format_secondary_markup(message)
        dialog.run()
        dialog.destroy()

    def load_cycles_components(self):

        # SWITCH ALERTS
        stat = str(int(config['CONFIGURATION']['alerts']))
        # active = None

        if stat == '1':
            self.switchAlerts.set_active(True)
        elif stat == '0':
            self.switchAlerts.set_active(False)
        print()

    def load_components(self, radiobutton1, radiobutton2, radiobutton3):

        print('\nLoading variables ...\n')

        variable = config['CONFIGURATION']['application_on']
        if variable == '1':
            self.switchOnOff.set_active(True)
            print('\tState: on')

        elif variable == '0':
            self.switchOnOff.set_active(False)
            print('\tState: off')

        # Autostart (system)
        variable = config['CONFIGURATION']['autostart']

        if (os.path.isfile(user_home + "/.config/autostart/slimbookbattery-autostart.desktop")):
            self.switchAutostart.set_active(True)
            self.autostart_inicial = '1'
            print('\tAutostart: on')
        else:
            self.switchAutostart.set_active(False)
            self.autostart_inicial = '0'
            print('\tAutostart: off')

        # Actual Mode ()
        config.read(user_home + '/.config/slimbookbattery/slimbookbattery.conf')
        variable = config['CONFIGURATION']['modo_actual']

        if variable == '1':
            radiobutton1.set_active(True)
            self.modo_actual = '1'
            print('\tMode: Low')

        elif variable == '2':
            radiobutton2.set_active(True)
            self.modo_actual = '2'
            print('\tMode: Medium')

        elif variable == '3':
            radiobutton3.set_active(True)
            self.modo_actual = '3'
            print('\tMode: High')

        # Work Mode (custom conf avocado)

        # Se mirará el archivo original de tlp para poder comprobar que modo tiene activo.
        # Esto se comprueba para poder devolver 0 o 1 y en el combobox poder
        # mostrar como seleccionado el que esta activo actualmente.
        # print('Loading workmode...')
        if subprocess.getstatusoutput("cat /etc/tlp.conf | grep 'TLP_DEFAULT_MODE=AC'")[0] == 0:
            print('\tWorkMode:  AC')
            self.comboBoxWorkMode.set_active(0)

        elif subprocess.getstatusoutput("cat /etc/tlp.conf | grep 'TLP_DEFAULT_MODE=BAT'")[0] == 0:
            print('\tWorkMode: BAT')
            self.comboBoxWorkMode.set_active(1)

        else:
            print('\tWorkMode: Not found')

        # Icon (.conf)

        variable = config['CONFIGURATION']['icono']

        if variable == '1':
            print('\tIcon: on')
            self.switchIcon.set_active(True)

        else:
            print('\tIcon: off')
            self.switchIcon.set_active(False)

        print()

    def write_modes_conf(self):

        mode = 'ahorrodeenergia'
        # print('\n\n*** '+mode.upper()+' CONFIGURATION ***\n')
        print(colors.GREEN + "\n['" + mode.upper() + "' CONFIGURATION]" + colors.ENDC)

        statLimitCPU = self.comboBoxLimitCPU.get_active_iter()  # .conf file && Tlp custom file*
        # Test pending
        if statLimitCPU is not None:
            model = self.comboBoxLimitCPU.get_model()
            row_id, name = model[statLimitCPU][:2]
            if name == (_('maximum')):
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=33' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=balance_performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')

                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))
                config.set('SETTINGS', 'limit_cpu_ahorro', '1')

            elif name == (_('medium')):

                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=80' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=balance_performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')
                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))
                config.set('SETTINGS', 'limit_cpu_ahorro', '2')

            elif name == (_('none')):
     
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')
                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))
                config.set('SETTINGS', 'limit_cpu_ahorro', '3')

        statGovernor = self.comboBoxGovernor.get_active_iter()  # .conf file && Tlp custom file*
        # Test pending
        if statGovernor is not None:
            model = self.comboBoxGovernor.get_model()
            row_id, name = model[statGovernor][:2]
            subprocess.getstatusoutput(
                'sed -i "/CPU_SCALING_GOVERNOR_ON_BAT=/ '
                'cCPU_SCALING_GOVERNOR_ON_BAT=' + name + '" ~/.config/slimbookbattery/custom/' + mode)

        statGraphics = self.switchGraphics.get_active()  # .conf file *
        if statGraphics:
            config.set('SETTINGS', 'graphics_ahorro', str(1))
        else:
            config.set('SETTINGS', 'graphics_ahorro', str(0))

        statSound = self.switchSound.get_active()  # Tlp custom file *

        if statSound:
            exec = subprocess.getstatusoutput(
                'sed -i "/SOUND_POWER_SAVE_ON_BAT=/ '
                'cSOUND_POWER_SAVE_ON_BAT=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting sound sving to ' + str(statSound) + ' --> Exit: ' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/SOUND_POWER_SAVE_ON_BAT=/ '
                'cSOUND_POWER_SAVE_ON_BAT=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting sound sving to ' + str(statSound) + ' --> Exit: ' + str(exec[0]))
        print(mode, str(exec), )

        statWifiPower = self.switchWifiPower.get_active()  # Tlp custom file *
        if statWifiPower:
            exec = subprocess.getstatusoutput(
                'sed -i "/WIFI_PWR_ON_BAT=/ cWIFI_PWR_ON_BAT=on" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting wifi sving to ' + str(statWifiPower) + ' --> Exit: ' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/WIFI_PWR_ON_BAT=/ cWIFI_PWR_ON_BAT=off" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting wifi sving to ' + str(statWifiPower) + ' --> Exit: ' + str(exec[0]))

        statBluetoothNIU = self.switchBluetoothNIU.get_active()
        statWifiNIU = self.switchWifiNIU.get_active()
        devices = ''

        if statBluetoothNIU:
            devices = 'bluetooth'
        if statWifiNIU and devices == '':
            devices = 'wifi'
        elif statWifiNIU:
            devices = devices + ' wifi'

        exec = subprocess.getstatusoutput(
            "sed -i '/DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE/ "
            "cDEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE=\"" + devices + "\"' ~/.config/slimbookbattery/custom/" + mode)
        print('Setting devices to disable when not in use: ' + devices + ' --> Exit:' + str(exec[0]))

        try:
            variable = self.switchTDP.get_name()
            statTDP = self.switchTDP.get_active()
            if statTDP:
                config.set('TDP', variable, '1')
                print('Setting devices TDP sync: 1 ')
            else:
                config.set('TDP', variable, '0')
                print('Setting devices TDP sync: 0 ')
        except Exception:
            print('Switch TDP not set')

        config.set('SETTINGS', 'ahorro_brightness', str(int(self.scaleBrightness.get_value())))

        brightness_switch = self.brightness_switch1.get_active()
        if brightness_switch:
            config.set('SETTINGS', 'saving_brightness_switch', '1')
            print('Setting brightnes switch to 1')
        else:
            config.set('SETTINGS', 'saving_brightness_switch', '0')
            print('Setting brightnes switch to 0')

        try:
            statAnimations = self.switchAnimations.get_active()
            if statAnimations:
                config.set('SETTINGS', 'ahorro_animations', '1')
            else:
                config.set('SETTINGS', 'ahorro_animations', '0')
        except Exception:
            print('Switch animations disabled')

        statBluetoothOS = self.switchBluetoothOS.get_active()  # Tlp custom file
        statWifiOS = self.switchWifiOS.get_active()
        devices = ''

        if statBluetoothOS:
            devices = 'bluetooth'
        if statWifiOS and devices == '':
            devices = 'wifi'
        elif statWifiOS:
            devices = devices + ' wifi'

        exec = subprocess.getstatusoutput(
            "sed -i '/DEVICES_TO_DISABLE_ON_STARTUP/ "
            "cDEVICES_TO_DISABLE_ON_STARTUP=\"" + devices + "\"' ~/.config/slimbookbattery/custom/" + mode)
        print('Setting devices to disable on startup: ' + devices + ' --> Exit:' + str(exec[0]))

        statWifiDisableLAN = self.switchWifiDisableLAN.get_active()  # Tlp custom file
        if statWifiDisableLAN:
            exec = subprocess.getstatusoutput('''
                sed -i '/DEVICES_TO_DISABLE_ON_LAN_CONNECT/ cDEVICES_TO_DISABLE_ON_LAN_CONNECT="wifi"' ~/.config/slimbookbattery/custom/''' + mode + '''
                sed -i '/DEVICES_TO_ENABLE_ON_LAN_DISCONNECT/ cDEVICES_TO_ENABLE_ON_LAN_DISCONNECT="wifi"' ~/.config/slimbookbattery/custom/''' + mode + '''
                ''')
            print('Setting disable wifi when LAN to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput('''
                sed -i '/DEVICES_TO_DISABLE_ON_LAN_CONNECT/ cDEVICES_TO_DISABLE_ON_LAN_CONNECT=""' ~/.config/slimbookbattery/custom/''' + mode + '''
                sed -i '/DEVICES_TO_ENABLE_ON_LAN_DISCONNECT/ cDEVICES_TO_ENABLE_ON_LAN_DISCONNECT=""' ~/.config/slimbookbattery/custom/''' + mode + '''
                ''')
            print('Setting disable wifi when LAN to off --> Exit:' + str(exec[0]))

        statUSBSuspend = self.switchUSBSuspend.get_active()
        if statUSBSuspend:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND=/ cUSB_AUTOSUSPEND=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND=/ cUSB_AUTOSUSPEND=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension to on --> Exit:' + str(exec[0]))

        textBlacklistUSBIDs = self.entryBlacklistUSBIDs.get_text()

        os.system(
            "sed -i '/USB_BLACKLIST=/ "
            "cUSB_BLACKLIST=\"" + textBlacklistUSBIDs + "\"' ~/.config/slimbookbattery/custom/" + mode)
        # os.system('sed -i "/USB_BLACKLIST=/ cUSB_BLACKLIST=\"'+
        #                    textBlacklistUSBIDs+'\"" ~/.config/slimbookbattery/custom/'+mode)
        print('Setting devices blacklist: ' + textBlacklistUSBIDs + ' --> Exit:' + str(exec[0]))

        statBlacklistBUSB = self.switchBlacklistBUSB.get_active()
        if statBlacklistBUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_BTUSB=/ cUSB_BLACKLIST_BTUSB=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting bluetooth exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_BTUSB=/ cUSB_BLACKLIST_BTUSB=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting bluetooth exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statBlacklistPrintUSB = self.switchBlacklistPrintUSB.get_active()
        if statBlacklistPrintUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_PRINTER=/ cUSB_BLACKLIST_PRINTER=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting printers exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_PRINTER=/ cUSB_BLACKLIST_PRINTER=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting printers exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statBlacklistWWANUSB = self.switchBlacklistWWANUSB.get_active()
        if statBlacklistWWANUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_WWAN=/ cUSB_BLACKLIST_WWAN=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting WWAN exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_WWAN=/ cUSB_BLACKLIST_WWAN=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting WWAN exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statShutdownSuspendUSB = self.switchShutdownSuspendUSB.get_active()
        if statShutdownSuspendUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=/ '
                'cUSB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension DISABLE ON SHUTDOWN to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=/ '
                'cUSB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension DISABLE ON SHUTDOWN to on --> Exit:' + str(exec[0]))

        print('\n')

        print('COnfig: ' + config['SETTINGS']['limit_cpu_ahorro'])

        # This step is done at the end of function
        configfile = open(user_home + '/.config/slimbookbattery/slimbookbattery.conf', 'w')
        config.write(configfile)
        configfile.close()

    def write_modes2_conf(self):

        mode = 'equilibrado'
        # print('\n\n*** '+mode.capitalize()+' CONFIGURATION ***\n')
        print(colors.GREEN + "\n['" + mode.upper() + "' CONFIGURATION]" + colors.ENDC)

        statLimitCPU = self.comboBoxLimitCPU2.get_active_iter()  # .conf file && Tlp custom file*
        # Test pending
        if statLimitCPU is not None:
            model = self.comboBoxLimitCPU2.get_model()
            row_id, name = model[statLimitCPU][:2]
            if name == (_('maximum')):
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=33' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=balance_performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')

                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))

                config.set('SETTINGS', 'limit_cpu_equilibrado', '1')

            elif name == (_('medium')):
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=80' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=balance_performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')
                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))
                config.set('SETTINGS', 'limit_cpu_equilibrado', '2')

            elif name == (_('none')):
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=100' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')
                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))
                config.set('SETTINGS', 'limit_cpu_equilibrado', '3')

        statGovernor = self.comboBoxGovernor2.get_active_iter()  # .conf file && Tlp custom file*
        # Test pending
        if statGovernor is not None:
            model = self.comboBoxGovernor2.get_model()
            row_id, name = model[statGovernor][:2]
            subprocess.getstatusoutput(
                'sed -i "/CPU_SCALING_GOVERNOR_ON_BAT=/ '
                'cCPU_SCALING_GOVERNOR_ON_BAT=' + name + '" ~/.config/slimbookbattery/custom/' + mode)

        statGraphics = self.switchGraphics2.get_active()  # .conf file *
        if statGraphics:
            config.set('SETTINGS', 'graphics_equilibrado', str(1))
        else:
            config.set('SETTINGS', 'graphics_equilibrado', str(0))

        statSound = self.switchSound2.get_active()  # Tlp custom file *
        if statSound:
            exec = subprocess.getstatusoutput(
                'sed -i "/SOUND_POWER_SAVE_ON_BAT=/ '
                'cSOUND_POWER_SAVE_ON_BAT=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting sound sving to ' + str(statSound) + ' --> Exit: ' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/SOUND_POWER_SAVE_ON_BAT=/ '
                'cSOUND_POWER_SAVE_ON_BAT=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting sound sving to ' + str(statSound) + ' --> Exit: ' + str(exec[0]))

        statWifiPower = self.switchWifiPower2.get_active()  # Tlp custom file *
        if statWifiPower:
            exec = subprocess.getstatusoutput(
                'sed -i "/WIFI_PWR_ON_BAT=/ cWIFI_PWR_ON_BAT=on" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting wifi sving to ' + str(statWifiPower) + ' --> Exit: ' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/WIFI_PWR_ON_BAT=/ cWIFI_PWR_ON_BAT=off" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting wifi sving to ' + str(statWifiPower) + ' --> Exit: ' + str(exec[0]))

        statBluetoothNIU = self.switchBluetoothNIU2.get_active()
        statWifiNIU = self.switchWifiNIU2.get_active()
        devices = ''

        if statBluetoothNIU:
            devices = 'bluetooth'
        if statWifiNIU and devices == '':
            devices = 'wifi'
        elif statWifiNIU:
            devices = devices + ' wifi'

        exec = subprocess.getstatusoutput(
            "sed -i '/DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE/ "
            "cDEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE=\"" + devices + "\"' ~/.config/slimbookbattery/custom/" + mode)
        print('Setting devices to disable when not in use: ' + devices + ' --> Exit:' + str(exec[0]))

        try:
            variable = self.switchTDP2.get_name()
            statTDP = self.switchTDP2.get_active()
            if statTDP:
                config.set('TDP', variable, '1')
                print('Setting devices TDP sync: 1 ')
            else:
                config.set('TDP', variable, '0')
                print('Setting devices TDP sync: 0 ')
        except Exception:
            print('Switch TDP not set')

        config.set('SETTINGS', 'equilibrado_brightness', str(int(self.scaleBrightness2.get_value())))
        brightness_switch = self.brightness_switch2.get_active()
        if brightness_switch:
            config.set('SETTINGS', 'balanced_brightness_switch', '1')
            print('Setting brightnes switch to 1')
        else:
            config.set('SETTINGS', 'balanced_brightness_switch', '0')
            print('Setting brightnes switch to 0')

        try:
            statAnimations = self.switchAnimations2.get_active()
            if statAnimations:
                config.set('SETTINGS', 'equilibrado_animations', '1')
            else:
                config.set('SETTINGS', 'equilibrado_animations', '0')
        except Exception:
            print('Switch animations disabled')

        statBluetoothOS = self.switchBluetoothOS2.get_active()  # Tlp custom file
        statWifiOS = self.switchWifiOS2.get_active()
        devices = ''

        if statBluetoothOS:
            devices = 'bluetooth'
        if statWifiOS and devices == '':
            devices = 'wifi'
        elif statWifiOS:
            devices = devices + ' wifi'

        exec = subprocess.getstatusoutput(
            "sed -i '/DEVICES_TO_DISABLE_ON_STARTUP/ "
            "cDEVICES_TO_DISABLE_ON_STARTUP=\"" + devices + "\"' ~/.config/slimbookbattery/custom/" + mode)
        print('Setting devices to disable on startup: ' + devices + ' --> Exit:' + str(exec[0]))

        statWifiDisableLAN = self.switchWifiDisableLAN2.get_active()  # Tlp custom file
        if statWifiDisableLAN:
            exec = subprocess.getstatusoutput('''
                sed -i '/DEVICES_TO_DISABLE_ON_LAN_CONNECT/ cDEVICES_TO_DISABLE_ON_LAN_CONNECT="wifi"' ~/.config/slimbookbattery/custom/''' + mode + '''
                sed -i '/DEVICES_TO_ENABLE_ON_LAN_DISCONNECT/ cDEVICES_TO_ENABLE_ON_LAN_DISCONNECT="wifi"' ~/.config/slimbookbattery/custom/''' + mode + '''
                ''')
            print('Setting disable wifi when LAN to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput('''
                sed -i '/DEVICES_TO_DISABLE_ON_LAN_CONNECT/ cDEVICES_TO_DISABLE_ON_LAN_CONNECT=""' ~/.config/slimbookbattery/custom/''' + mode + '''
                sed -i '/DEVICES_TO_ENABLE_ON_LAN_DISCONNECT/ cDEVICES_TO_ENABLE_ON_LAN_DISCONNECT=""' ~/.config/slimbookbattery/custom/''' + mode + '''
                ''')
            print('Setting disable wifi when LAN to off --> Exit:' + str(exec[0]))

        statUSBSuspend = self.switchUSBSuspend2.get_active()
        if statUSBSuspend:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND=/ cUSB_AUTOSUSPEND=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND=/ cUSB_AUTOSUSPEND=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension to on --> Exit:' + str(exec[0]))

        textBlacklistUSBIDs = self.entryBlacklistUSBIDs.get_text()

        os.system(
            "sed -i '/USB_BLACKLIST=/ cUSB_BLACKLIST=\"{}\"' ~/.config/slimbookbattery/custom/{}".format(
                textBlacklistUSBIDs, mode
            )
        )
        # os.system('sed -i "/USB_BLACKLIST=/ cUSB_BLACKLIST=\"'+
        #                    textBlacklistUSBIDs+'\"" ~/.config/slimbookbattery/custom/'+mode)
        print('Setting devices blacklist: ' + textBlacklistUSBIDs + ' --> Exit:' + str(exec[0]))

        statBlacklistBUSB = self.switchBlacklistBUSB2.get_active()
        if statBlacklistBUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_BTUSB=/ cUSB_BLACKLIST_BTUSB=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting bluetooth exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_BTUSB=/ cUSB_BLACKLIST_BTUSB=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting bluetooth exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statBlacklistPrintUSB = self.switchBlacklistPrintUSB2.get_active()
        if statBlacklistPrintUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_PRINTER=/ cUSB_BLACKLIST_PRINTER=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting printers exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_PRINTER=/ cUSB_BLACKLIST_PRINTER=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting printers exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statBlacklistWWANUSB = self.switchBlacklistWWANUSB2.get_active()
        if statBlacklistWWANUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_WWAN=/ cUSB_BLACKLIST_WWAN=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting WWAN exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_WWAN=/ cUSB_BLACKLIST_WWAN=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting WWAN exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statShutdownSuspendUSB = self.switchShutdownSuspendUSB2.get_active()
        if statShutdownSuspendUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=/ '
                'cUSB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension DISABLE ON SHUTDOWN to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=/ '
                'cUSB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension DISABLE ON SHUTDOWN to on --> Exit:' + str(exec[0]))

        print('\n')

        # This step is done at the end of function
        configfile = open(user_home + '/.config/slimbookbattery/slimbookbattery.conf', 'w')
        config.write(configfile)
        configfile.close()

    def write_modes3_conf(self):
        mode = 'maximorendimiento'
        # print('\n\n*** '+mode.capitalize()+' CONFIGURATION ***\n')
        print(colors.GREEN + "\n['" + mode.upper() + "' CONFIGURATION]" + colors.ENDC)

        statLimitCPU = self.comboBoxLimitCPU3.get_active_iter()  # .conf file && Tlp custom file*
        # Test pending
        if statLimitCPU is not None:
            model = self.comboBoxLimitCPU3.get_model()
            row_id, name = model[statLimitCPU][:2]
            if name == (_('maximum')):
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=33' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=balance_performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')

                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))

                config.set('SETTINGS', 'limit_cpu_maximorendimiento', '1')

            elif name == (_('medium')):
                # os.system('/usr/share/slimbookbattery/bin/limitcpu.x 2')
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=80' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=balance_performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')
                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))
                config.set('SETTINGS', 'limit_cpu_maximorendimiento', '2')

            elif name == (_('none')):
                # os.system('/usr/share/slimbookbattery/bin/limitcpu.x 3')
                exec = subprocess.getstatusoutput('''
                    sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_AC/ cCPU_MAX_PERF_ON_AC=100' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_MIN_PERF_ON_BAT/ cCPU_MIN_PERF_ON_BAT=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_MAX_PERF_ON_BAT/ cCPU_MAX_PERF_ON_BAT=100' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_AC/ cCPU_BOOST_ON_AC=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_BOOST_ON_BAT/ cCPU_BOOST_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/CPU_HWP_ON_AC/ cCPU_HWP_ON_AC=performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/CPU_HWP_ON_BAT/ cCPU_HWP_ON_BAT=power' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/ENERGY_PERF_POLICY_ON_AC/ cENERGY_PERF_POLICY_ON_AC=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/ENERGY_PERF_POLICY_ON_BAT/ cENERGY_PERF_POLICY_ON_BAT=balance-performance' ~/.config/slimbookbattery/custom/''' + mode + '''

                    sed -i '/SCHED_POWERSAVE_ON_AC/ cSCHED_POWERSAVE_ON_AC=0' ~/.config/slimbookbattery/custom/''' + mode + '''
                    sed -i '/SCHED_POWERSAVE_ON_BAT/ cSCHED_POWERSAVE_ON_BAT=1' ~/.config/slimbookbattery/custom/''' + mode + '''
                    ''')
                print('Setting limit to ' + name + ' --> Exit: ' + str(exec[0]))
                config.set('SETTINGS', 'limit_cpu_maximorendimiento', '3')

        statGovernor = self.comboBoxGovernor3.get_active_iter()  # .conf file && Tlp custom file*
        # Test pending
        if statGovernor is not None:
            model = self.comboBoxGovernor3.get_model()
            row_id, name = model[statGovernor][:2]
            subprocess.getstatusoutput(
                'sed -i "/CPU_SCALING_GOVERNOR_ON_BAT=/ '
                'cCPU_SCALING_GOVERNOR_ON_BAT=' + name + '" ~/.config/slimbookbattery/custom/' + mode)

        statSound = self.switchSound3.get_active()  # Tlp custom file *
        if statSound:
            exec = subprocess.getstatusoutput(
                'sed -i "/SOUND_POWER_SAVE_ON_BAT=/ '
                'cSOUND_POWER_SAVE_ON_BAT=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting sound sving to ' + str(statSound) + ' --> Exit: ' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/SOUND_POWER_SAVE_ON_BAT=/ '
                'cSOUND_POWER_SAVE_ON_BAT=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting sound sving to ' + str(statSound) + ' --> Exit: ' + str(exec[0]))

        statWifiPower = self.switchWifiPower3.get_active()  # Tlp custom file *
        if statWifiPower:
            exec = subprocess.getstatusoutput(
                'sed -i "/WIFI_PWR_ON_BAT=/ cWIFI_PWR_ON_BAT=on" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting wifi sving to ' + str(statWifiPower) + ' --> Exit: ' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/WIFI_PWR_ON_BAT=/ cWIFI_PWR_ON_BAT=off" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting wifi sving to ' + str(statWifiPower) + ' --> Exit: ' + str(exec[0]))

        statBluetoothNIU = self.switchBluetoothNIU3.get_active()
        statWifiNIU = self.switchWifiNIU3.get_active()
        devices = ''

        if statBluetoothNIU:
            devices = 'bluetooth'
        if statWifiNIU and devices == '':
            devices = 'wifi'
        elif statWifiNIU:
            devices = devices + ' wifi'

        exec = subprocess.getstatusoutput(
            "sed -i '/DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE/ "
            "cDEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE=\"" + devices + "\"' ~/.config/slimbookbattery/custom/" + mode)
        print('Setting devices to disable when not in use: ' + devices + ' --> Exit:' + str(exec[0]))

        try:
            variable = self.switchTDP3.get_name()
            statTDP = self.switchTDP3.get_active()
            if statTDP:
                config.set('TDP', variable, '1')
                print('Setting devices TDP sync: 1 ')
            else:
                config.set('TDP', variable, '0')
                print('Setting devices TDP sync: 0 ')
        except Exception:
            print('Switch TDP not set')

        value = (str(int(self.scaleBrightness3.get_value())))
        config.set('SETTINGS', 'maxrendimiento_brightness', value)
        print('Setting brigtness')

        brightness_switch = self.brightness_switch3.get_active()
        if brightness_switch:
            config.set('SETTINGS', 'power_brightness_switch', '1')
            print('Setting brightnes switch to 1')
        else:
            config.set('SETTINGS', 'power_brightness_switch', '0')
            print('Setting brightnes switch to 0')

        try:
            statAnimations = self.switchAnimations3.get_active()
            if statAnimations:
                config.set('SETTINGS', 'maxrendimiento_animations', '1')
            else:
                config.set('SETTINGS', 'maxrendimiento_animations', '0')
        except Exception:
            print('Switch animations disabled')

        statWifiNIU = self.switchWifiNIU3.get_active()

        statBluetoothOS = self.switchBluetoothOS3.get_active()  # Tlp custom file
        statWifiOS = self.switchWifiOS3.get_active()
        devices = ''

        if statBluetoothOS:
            devices = 'bluetooth'
        if statWifiOS and devices == '':
            devices = 'wifi'
        elif statWifiOS:
            devices = devices + ' wifi'

        exec = subprocess.getstatusoutput(
            "sed -i '/DEVICES_TO_DISABLE_ON_STARTUP/ "
            "cDEVICES_TO_DISABLE_ON_STARTUP=\"" + devices + "\"' ~/.config/slimbookbattery/custom/" + mode)
        print('Setting devices to disable on startup: ' + devices + ' --> Exit:' + str(exec[0]))

        statWifiDisableLAN = self.switchWifiDisableLAN3.get_active()  # Tlp custom file
        if statWifiDisableLAN:
            exec = subprocess.getstatusoutput('''
                sed -i '/DEVICES_TO_DISABLE_ON_LAN_CONNECT/ cDEVICES_TO_DISABLE_ON_LAN_CONNECT="wifi"' ~/.config/slimbookbattery/custom/''' + mode + '''
	            sed -i '/DEVICES_TO_ENABLE_ON_LAN_DISCONNECT/ cDEVICES_TO_ENABLE_ON_LAN_DISCONNECT="wifi"' ~/.config/slimbookbattery/custom/''' + mode + '''
                ''')
            print('Setting disable wifi when LAN to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput('''
                sed -i '/DEVICES_TO_DISABLE_ON_LAN_CONNECT/ cDEVICES_TO_DISABLE_ON_LAN_CONNECT=""' ~/.config/slimbookbattery/custom/''' + mode + '''
	            sed -i '/DEVICES_TO_ENABLE_ON_LAN_DISCONNECT/ cDEVICES_TO_ENABLE_ON_LAN_DISCONNECT=""' ~/.config/slimbookbattery/custom/''' + mode + '''
                ''')
            print('Setting disable wifi when LAN to off --> Exit:' + str(exec[0]))

        statUSBSuspend = self.switchUSBSuspend3.get_active()
        if statUSBSuspend:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND=/ cUSB_AUTOSUSPEND=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND=/ cUSB_AUTOSUSPEND=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension to on --> Exit:' + str(exec[0]))

        textBlacklistUSBIDs = self.entryBlacklistUSBIDs.get_text()

        os.system(
            "sed -i '/USB_BLACKLIST=/ cUSB_BLACKLIST=\"{}\"' ~/.config/slimbookbattery/custom/{}".format(
                textBlacklistUSBIDs, mode
            ))
        # os.system('sed -i "/USB_BLACKLIST=/ cUSB_BLACKLIST=\"'+
        #                   textBlacklistUSBIDs+'\"" ~/.config/slimbookbattery/custom/'+mode)
        print('Setting devices blacklist: ' + textBlacklistUSBIDs + ' --> Exit:' + str(exec[0]))

        statBlacklistBUSB = self.switchBlacklistBUSB3.get_active()
        if statBlacklistBUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_BTUSB=/ cUSB_BLACKLIST_BTUSB=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting bluetooth exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_BTUSB=/ cUSB_BLACKLIST_BTUSB=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting bluetooth exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statBlacklistPrintUSB = self.switchBlacklistPrintUSB3.get_active()
        if statBlacklistPrintUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_PRINTER=/ cUSB_BLACKLIST_PRINTER=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting printers exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_PRINTER=/ cUSB_BLACKLIST_PRINTER=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting printers exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statBlacklistWWANUSB = self.switchBlacklistWWANUSB3.get_active()
        if statBlacklistWWANUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_WWAN=/ cUSB_BLACKLIST_WWAN=1" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting WWAN exclusion from USB Suspension to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_BLACKLIST_WWAN=/ cUSB_BLACKLIST_WWAN=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting WWAN exclusion from USB Suspension to off --> Exit:' + str(exec[0]))

        statShutdownSuspendUSB = self.switchShutdownSuspendUSB3.get_active()
        if statShutdownSuspendUSB:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=/ cUSB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=1" '
                '~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension DISABLE ON SHUTDOWN to on --> Exit:' + str(exec[0]))
        else:
            exec = subprocess.getstatusoutput(
                'sed -i "/USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=/ '
                'cUSB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=0" ~/.config/slimbookbattery/custom/' + mode)
            print('Setting USB Suspension DISABLE ON SHUTDOWN to on --> Exit:' + str(exec[0]))

        print('\n')

        # This step is done at the end of function
        configfile = open(user_home + '/.config/slimbookbattery/slimbookbattery.conf', 'w')
        config.write(configfile)
        configfile.close()

    def animations(self, mode):

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
                print('xd')
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

    def close_ok(self, button):
        self.apply_conf()
        exit(0)

    def apply_conf(self):
        print('\nClosing window ...')

        # Saving interface general values **********************************************************

        state = ''
        autostart = ''
        workMode = ''
        icono = ''

        # Leemos switches y guardamos en variables

        # State
        if self.switchOnOff.get_state():
            print('\tState: on')
            state = '1'
        else:
            print('\tState: off')
            state = '0'
            self.animations('0')  # We enable animations

        # Autostart
        if self.switchAutostart.get_state():
            print('\tAutostart: on')
            autostart = '1'
        else:
            print('\tAutostart: off')
            autostart = '0'

        # Modo
        # print(self.modo_actual)

        if self.modo_actual == '1':
            print('\tMode: Low')
            # mode = 'ahorrodeenergia'

        elif self.modo_actual == '2':
            print('\tMode: Mid')
            # mode = 'equilibrado'

        elif self.modo_actual == '3':
            print('\tMode: High')
            # mode = 'maximorendimiento'

        else:
            print('Err: Could not get mode')

        # Work Mode
        iter = self.comboBoxWorkMode.get_active_iter()

        if iter is not None:
            model = self.comboBoxWorkMode.get_model()
            row_id, name = model[iter][:2]

            if name != self.workMode:
                print('\n\n')
                workMode = name

            if not workMode == '':
                print('Setting workmode ' + workMode + '...')
                # exec = subprocess.getstatusoutput("sed -i '/CPU_MIN_PERF_ON_AC/ cCPU_MIN_PERF_ON_AC=0' /etc/tlp.conf")
                subprocess.getstatusoutput(
                    'pkexec slimbookbattery-pkexec change_config TLP_DEFAULT_MODE ' + workMode)

        # Icon
        if self.switchIcon.get_state():
            # print('\tIcon: on')
            icono = '1'
        else:
            # print('\tIcon: off')
            icono = '0'

        # ACTIONS General **************************************************************************

        # Checking autostart

        if autostart == '1' and self.autostart_inicial == '0':
            print('Enabling autostart ...')
            if os.path.isfile('~/.config/autostart'):
                print(subprocess.getoutput(
                    "cp /usr/share/slimbookbattery/src/slimbookbattery-autostart.desktop ~/.config/autostart/"))
            else:
                subprocess.getoutput('mkdir ~/.config/autostart')
                print(subprocess.getoutput(
                    "cp /usr/share/slimbookbattery/src/slimbookbattery-autostart.desktop ~/.config/autostart/"))

        elif autostart == '0' and self.autostart_inicial == '1':
            print('Disabling autostart ...')
            os.system("rm -rf ~/.config/autostart/slimbookbattery-autostart.desktop")

        # UPDATING .CONF

        config.set('CONFIGURATION', 'icono', icono)

        config.set('CONFIGURATION', 'application_on', state)

        config.set('CONFIGURATION', 'modo_actual', self.modo_actual)

        configfile = open(user_home + '/.config/slimbookbattery/slimbookbattery.conf', 'w')
        config.write(configfile)
        configfile.close()

        print('pkexec slimbookbattry-pkexec change_config TLP_DEFAULT_MODE ' + workMode)

        # Mode setting
        print()
        fichero = user_home + '/.config/slimbookbattery/slimbookbattery.conf'
        config.read(fichero)

        # Saving interface new values **************************************************************

        # Solo cambia en el conf.

        print('Switch alerts: ' + str(self.switchAlerts.get_state()))
        if self.switchAlerts.get_state():
            config.set('CONFIGURATION', 'alerts', str(1))
        else:
            config.set('CONFIGURATION', 'alerts', str(0))

        config.set('CONFIGURATION', 'max_battery_value', str(int(self.scaleMaxBatVal.get_value())))
        config.set('CONFIGURATION', 'min_battery_value', str(int(self.scaleMinBatVal.get_value())))
        config.set('CONFIGURATION', 'max_battery_times', str(int(self.scaleNumTimes.get_value())))
        config.set('CONFIGURATION', 'time_between_warnings', str(int(self.scaleTimeWarnings.get_value())))

        configfile = open(user_home + '/.config/slimbookbattery/slimbookbattery.conf', 'w')
        config.write(configfile)
        configfile.close()

        self.write_modes_conf()
        self.write_modes2_conf()
        self.write_modes3_conf()

        self.animations(config['CONFIGURATION']['modo_actual'])

        # Settings application
        command = 'pkexec slimbookbattery-pkexec apply'
        subprocess.Popen(command.split(' '))

        reboot_process('slimbookbatteryindicator.py', currpath + '/slimbookbatteryindicator.py', True)

        # This process wil only reboot if is running if not, and option is on, it will be launched
        actual_mode = config['CONFIGURATION']['modo_actual']

        tdpcontroller = config['TDP']['tdpcontroller']

        if actual_mode == '1':
            if config['TDP']['saving_tdpsync'] == '1':
                reboot_process(tdpcontroller + 'indicator.py',
                               '/usr/share/' + tdpcontroller + '/src/' + tdpcontroller + 'indicator.py', True)
        elif actual_mode == '2':
            if config['TDP']['balanced_tdpsync'] == '1':
                reboot_process(tdpcontroller + 'indicator.py',
                               '/usr/share/' + tdpcontroller + '/src/' + tdpcontroller + 'indicator.py', True)
        elif actual_mode == '3':
            if config['TDP']['power_tdpsync'] == '1':
                reboot_process(tdpcontroller + 'indicator.py',
                               '/usr/share/' + tdpcontroller + '/src/' + tdpcontroller + 'indicator.py', True)
        else:
            print('Mode not setting TDP')

    def on_buttonReportFile_clicked(self, buttonReportFile):
        # Se abrirá un dialogo para el usuario para que
        # elija donde desea guardar el archivo del reporte que se va a generar
        saveDialog = Gtk.FileChooserDialog(title="Please select a folder to save the file",
                                           parent=self,
                                           action=Gtk.FileChooserAction.SELECT_FOLDER)

        saveDialog.add_button(Gtk.STOCK_CANCEL, 0)
        saveDialog.add_button(Gtk.STOCK_SAVE, 1)

        response = saveDialog.run()
        saveDialog.set_name('save_dialog')
        if response == Gtk.ResponseType.OK:
            ruta = saveDialog.get_filename() + '/report_' + time.strftime("%d-%m-%y_%H:%M") + '.txt'
            escritorio = subprocess.getoutput("echo $XDG_CURRENT_DESKTOP")
            if subprocess.getstatusoutput(
                    "pkexec slimbookbattery-pkexec report " + ruta + ' ' + escritorio + ' ' + user_home)[0] == 0:
                print(_('Report file generated'))
            else:
                print(_('Report file canceled'))
        elif response == Gtk.ResponseType.CANCEL:
            print(_('Report file canceled'))
        saveDialog.destroy()

    def close(self, button, state):
        print('Button Close Clicked')
        Gtk.main_quit()
        exit(0)

    def update_config(self, section, variable, value):

        fichero = user_home + '/.config/slimbookbattery/slimbookbattery.conf'
        config.read(fichero)

        # We change our variable: config.set(section, variable, value)
        config.set(str(section), str(variable), str(value))

        # Writing our configuration file
        with open(fichero, 'w') as configfile:
            config.write(configfile)

        print("\n- Variable |" + variable + "| updated in .conf, actual value: " + value)


def governorIsCompatible():
    governor = subprocess.getoutput(
        'for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_driver; do cat $i; done').split('\n')
    governorCompatible = True
    governor_name = ''
    for governor_driver in governor:
        governor_name = governor_driver

        if governor_driver != 'intel_pstate' and governor_driver != 'acpi-cpufreq':
            governorCompatible = False
            break

    return governorCompatible, governor_name


def reboot_process(process_name, path, start):
    print('Rebooting ' + process_name + ' ...')
    # print(path)
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

    else:
        print(process_name + ' was not running')

        if start:
            print('Launching process...')
            if os.system('python3 ' + path + '  &') == 0:
                print('Done')
            else:
                print("Couldn't launch process")

    print()


style_provider = Gtk.CssProvider()
style_provider.load_from_path(currpath + '/css/style.css')

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

if __name__ == "__main__":
    win = Preferences()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
