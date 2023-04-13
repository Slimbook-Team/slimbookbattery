#!/usr/bin/env python3
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

import gi
import configparser
import logging
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

# We want load first current location
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
if CURRENT_PATH not in sys.path:
    sys.path = [CURRENT_PATH] + sys.path
import utils
import tdp_utils

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

logger = logging.getLogger()

USER_NAME = utils.get_user()
HOMEDIR = os.path.expanduser(f'~{USER_NAME}')
SESSION_TYPE = os.environ.get('XDG_SESSION_TYPE')

VTE_VERSION = subprocess.getstatusoutput('apt show gir1.2-vte-2.91 | grep Version')

UPDATES_DIR = os.path.join(CURRENT_PATH, 'updates', '_updates')
IMAGES_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '..', 'images'))
CONFIG_FOLDER = os.path.join(HOMEDIR, '.config/slimbookbattery')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'slimbookbattery.conf')

tdp_controller = tdp_utils.get_tdp_controller()

INTEL_ES = 'https://slimbook.es/es/tutoriales/aplicaciones-slimbook/515-slimbook-intel-controller'
INTEL_EN = 'https://slimbook.es/en/tutoriales/aplicaciones-slimbook/514-en-slimbook-intel-controller'
AMD_ES = 'https://slimbook.es/es/tutoriales/aplicaciones-slimbook/493-slimbook-amd-controller'
AMD_EN = 'https://slimbook.es/en/tutoriales/aplicaciones-slimbook/494-slimbook-amd-controller-en'

TLP_CONF, TLP_VERSION = utils.get_tlp_conf_file()

_ = utils.load_translation('preferences')

lang = utils.get_languages()[0]

config = configparser.ConfigParser()
# Add section to prevent configparser.NoSectionError when save
for section in ['TDP', 'CONFIGURATION', 'SETTINGS']:
    config.add_section(section)

if not os.path.isfile(CONFIG_FILE):
    try:
        import check_config  # Fix config and reload

        check_config.main()
    except Exception:
        logger.exception('Error fixing config file')

config.read(CONFIG_FILE)

class Colors:  # You may need to change color settings
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    CYAN = "\033[1;36m"
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    BOLD = "\033[;1m"
    BOLD = "\033[;1m"

class BasePageGrid(Gtk.Grid):
    tab_name = None
    allow_minimize = True
    SUPER_KWARGS = {
        'column_homogeneous': True,
        'column_spacing': 0,
        'row_spacing': 20,
    }
    GRID_KWARGS = {
        'column_homogeneous': True,
        'column_spacing': 0,
        'row_spacing': 15,
    }

    def __init__(self, parent, *args, **kwargs):
        kwargs.update(self.SUPER_KWARGS)
        super(BasePageGrid, self).__init__(*args, **kwargs)
        self.parent = parent
        self.content = {}
        self.grid = Gtk.Grid(**self.GRID_KWARGS)
        self.setup()
        self.complete_values()

    def get_page(self):
        if not (self.allow_minimize and self.parent.min_resolution):
            return self
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        scrolled_window.set_min_content_height(400)
        scrolled_window.set_min_content_width(1000)

        scrolled_window.add_with_viewport(self)
        return scrolled_window

    def setup(self):
        """
            Create the items inside the page
        """
        raise NotImplementedError()

    def complete_values(self):
        """
            Complete the content of the page
        """
        pass

    def manage_events(self, button, *args):
        """
            Function where received events
            :param button: Gtk objects that receive the event
            :param args: Depends of the event
        """
        pass

    def save_selection(self):
        """
            Save options to storage
        """
        pass

class InfoPageGrid(BasePageGrid):
    tab_name = _('Information')
    SOCIAL = [
        {
            'icon': 'twitter.png',
            'url': 'https://twitter.com/SlimbookEs',
            'text': '@SlimbookEs',
            'name': 'twitter',
        },
        {
            'icon': 'facebook.png',
            'url': 'https://www.facebook.com/slimbook.es',
            'text': 'Slimbook',
            'name': 'facebook',
        },
        {
            'icon': 'insta.png',
            'url': 'https://www.instagram.com/slimbookes/?hl=en',
            'text': 'Slimbook',
            'name': 'instagram',
        }
    ]

    def setup(self):
        self.setup_title()
        self.setup_description()
        self.setup_social()
        self.setup_disclaimer()
        self.setup_links()
        self.setup_contact()
        self.setup_licence()

        self.attach(self.grid, 0, 0, 2, 4)

    def setup_title(self):
        box = Gtk.HBox(spacing=15)
        box.set_halign(Gtk.Align.CENTER)

        # Title
        title = Gtk.Label(label='')
        title.set_markup('<span font="20"><b>Slimbook Battery 4</b></span>')
        title.set_justify(Gtk.Justification.CENTER)
        box.add(title)

        # Icon
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'normal.png'),
            width=60,
            height=60,
            preserve_aspect_ratio=True)
        box.add(Gtk.Image.new_from_pixbuf(pixbuf))
        self.grid.attach(box, 0, 1, 5, 1)

    def setup_description(self):
        line = Gtk.Label(label='')
        msg = "<span>{}\n{}</span>".format(
            _("Slimbook Battery is a battery optimization application for "
              "portable devices and can increase the battery"),
            _("life up to 50%. For this purpose, the third-party software is "
              "used to manage and configure the system resources.")
        )
        line.set_markup(msg)
        line.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(line, 0, 2, 5, 1)

        thanks = Gtk.Label(label='')
        thanks.set_markup("<span>" + (
            _("Special thanks to TLP (© 2019, linrunner), Nvidia, AMD and Intel "
              "for offering us the necessary tools to make it possible!")) + "</span>")
        thanks.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(thanks, 0, 3, 5, 1)

    def setup_social(self):
        line = Gtk.Label(label='')
        line.set_markup("<span>" + (
            _("If this application has been useful to you, "
              "consider saying it in our social networks or even buy a SLIMBOOK ;)")) + "</span>")
        line.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(line, 0, 4, 5, 1)
        box = Gtk.HBox(spacing=5)
        for social in self.SOCIAL:
            icon = Gtk.Image.new_from_pixbuf(
                GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename=os.path.join(IMAGES_PATH, social.get('icon')),
                    width=25,
                    height=25,
                    preserve_aspect_ratio=True
                )
            )
            icon.set_name('{name}_icon'.format(**social))
            box.pack_start(icon, False, False, 0)
            label = Gtk.Label(label=' ')
            markup = '<span><b><a href="{url}">{text}</a></b></span>'.format(**social)
            label.set_name(social.get('name'))
            label.set_markup(markup)
            label.set_justify(Gtk.Justification.CENTER)
            box.pack_start(label, False, False, 0)
        box.set_halign(Gtk.Align.CENTER)
        self.grid.attach(box, 0, 6, 5, 1)

    def setup_disclaimer(self):
        disclaimer = Gtk.Label(label='')
        msg = "<span><b>{}</b>{}\n{}</span>".format(
            _("IMPORTANT NOTE:"),
            _(" If you have any software, widget or application that changes the CPU profile, battery"),
            _("optimization or similar, it may affect the operation of this application. "
              "Use it under your responsibility.")
        )
        disclaimer.set_markup(msg)
        disclaimer.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(disclaimer, 0, 7, 5, 1)

    def setup_links(self):
        box = Gtk.HBox()
        box.set_halign(Gtk.Align.CENTER)

        link = Gtk.LinkButton(uri='https://slimbook.es/', label=(_('Visit SLIMBOOK website')))
        link.set_name('link')
        link.set_halign(Gtk.Align.CENTER)
        box.add(link)

        link = Gtk.LinkButton(uri=(_('strurlwebsite')), label=(_('Tutorial to learn to use Slimbook Battery')))
        link.set_name('link')
        link.set_halign(Gtk.Align.CENTER)
        box.add(link)

        link = Gtk.LinkButton(uri="https://github.com/slimbook/slimbookbattery/tree/main/src/translations",
                              label=(_('Help us with translations!')))
        link.set_name('link')
        link.set_halign(Gtk.Align.CENTER)
        box.add(link)
        self.grid.attach(box, 0, 10, 5, 1)

        box = Gtk.HBox()
        box.set_halign(Gtk.Align.CENTER)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'GitHub_Logo_White.png'),
            width=150,
            height=30,
            preserve_aspect_ratio=True)
        icon = Gtk.Image()
        icon.set_from_pixbuf(pixbuf)
        github = Gtk.LinkButton(uri="https://github.com/slimbook/slimbookbattery")
        github.set_name('link')
        github.set_halign(Gtk.Align.CENTER)
        github.set_image(icon)
        box.add(github)
        self.grid.attach(box, 0, 11, 5, 1)

        patreon = Gtk.Label()
        msg = "<span>{}<a href='https://www.patreon.com/slimbook'>Patreon</a>{}</span>".format(
            _("If you want you can support the developement of this app "
              "and several more to come by joining us on "),
            _(" or buying a brand new Slimbook ;)")
        )
        patreon.set_markup(msg)
        patreon.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(patreon, 0, 12, 5, 1)

    def setup_contact(self):
        info = Gtk.Label(label='')
        msg = "<span><b>{}</b> {} {} {}</span>".format(
            _("Info:"),
            _("Contact with us if you find something wrong. "), ('(dev@slimbook.es)'),
            _("\nWe would appreciate that you attach the file that is generated"),
            _("by clicking the button below")
        )
        info.set_markup(msg)
        info.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(info, 0, 13, 5, 1)

        info = Gtk.Label(label=' ')
        info.set_markup("<span><b>" + (_("Send an e-mail to: ")) + "dev@slimbook.es</b></span>")
        info.set_justify(Gtk.Justification.CENTER)

        box = Gtk.HBox()
        report = Gtk.Button(label=(_('Generate report file')))
        report.connect("clicked", self.manage_events)
        report.set_halign(Gtk.Align.CENTER)
        box.add(report)
        self.grid.attach(box, 1, 15, 3, 1)

    def setup_licence(self):
        licence = Gtk.Label(label='')
        licence.set_markup(_('The software is provided  as is , without warranty of any kind.'))
        licence.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(licence, 0, 16, 5, 1)

        box = Gtk.HBox()
        box.set_halign(Gtk.Align.CENTER)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'cc.png'),
            width=150,
            height=30,
            preserve_aspect_ratio=True)
        icon = Gtk.Image()
        icon.set_from_pixbuf(pixbuf)
        link = Gtk.LinkButton(uri="https://creativecommons.org/licenses/by-nc-nd/4.0/")
        link.set_name('link')
        link.set_halign(Gtk.Align.CENTER)
        link.set_image(icon)
        box.add(link)
        self.grid.attach(box, 0, 17, 5, 1)

    def manage_events(self, button, *args):
        save_dialog = Gtk.FileChooserDialog(title="Please select a folder to save the file",
                                            parent=self.parent,
                                            action=Gtk.FileChooserAction.SELECT_FOLDER)

        save_dialog.add_button(Gtk.STOCK_CANCEL, 0)
        save_dialog.add_button(Gtk.STOCK_SAVE, 1)
        save_dialog.set_name('save_dialog')

        response = save_dialog.run()
        if response == 1:
            path = os.path.join(save_dialog.get_filename(), f'report_{time.strftime("%d-%m-%y_%H:%M")}.txt')
            desktop = os.environ.get("XDG_CURRENT_DESKTOP")

            cmd = "pkexec slimbookbattery-pkexec report {path} {desktop} {user_home}".format(
                path=path, desktop=desktop, user_home=HOMEDIR
            )
            code, output = subprocess.getstatusoutput(cmd)
            if code == 0:
                logger.info(_('Report file generated'))
            else:
                logger.info(_('Report fail'))
                logger.error(output)
        elif response == Gtk.ResponseType.CANCEL:
            logger.info(_('Report file canceled'))
        save_dialog.destroy()

class BatteryGrid(BasePageGrid):
    tab_name = _('Battery')
    GRID_KWARGS = {
        'column_homogeneous': True,
        'column_spacing': 0,
        'row_spacing': 20,
        'halign': Gtk.Align.CENTER,
    }
    HEADER = 1
    CONTENT = 3

    TIME_TO_MAPPING = {
        'discharging': {
            'header': _('Time to empty:'),
            'filter': 'time to empty',
        },
        'charging': {
            'header': _('Time to full:'),
            'filter': 'time to full',
        },
        'fully-charged': {
            'header': _('Time to full:'),
            'text': _('Fully charged'),
        },
    }

    UPDATE_FIELDS = [
        ('percentage', 'percentage'),
        ('voltage', 'voltage'),
        ('rate', 'energy-rate'),
        ('state', 'state'),
        ('updated', 'updated'),
    ]

    FIELDS = [
        {
            'label_name': 'native',
            'header': _('Battery'),
            'filter': 'native-path',
        },
        {
            'label_name': 'vendor',
            'header': _('Manufacturer:'),
            'filter': 'vendor',
        },
        {
            'label_name': 'model',
            'header': _('Battery model:'),
            'filter': 'model',
        },
        {
            'label_name': 'technology',
            'header': _('Technology:'),
            'filter': 'technology',
        },
        {
            'label_name': 'percentage',
            'header': _('Remaining battery:'),
            'filter': 'percentage',
        },
        {
            'label_name': 'capacity',
            'header': _('Maximum capacity:'),
            'filter': 'capacity',
        },
        {
            'label_name': 'state',
            'header': _('Status:'),
            'filter': 'state',
        },
        {
            'label_name': 'time_to',
            'mapping': TIME_TO_MAPPING,
        },
        {
            'label_name': 'rechargeable',
            'header': _('Rechargeable:'),
            'filter': 'rechargeable',
        },
        {
            'label_name': 'supply',
            'header': _('Power supply:'),
            'filter': 'power supply',
        },
        {
            'label_name': 'full',
            'header': _('Energy full:'),
            'filter': 'energy-full',
        },
        {
            'label_name': 'design',
            'header': _('Energy full design:'),
            'filter': 'energy-full-design',
        },
        {
            'label_name': 'rate',
            'header': _('Energy rate:'),
            'filter': 'energy-rate',
        },
        {
            'label_name': 'voltage',
            'header': _('Voltage:'),
            'filter': 'voltage',
        },
        {
            'label_name': 'updated',
            'header': _('Last update of the battery information:'),
            'filter': 'updated',
        },
    ]

    def __init__(self, parent, *args, **kwargs):
        self.time_to_header = None
        super(BatteryGrid, self).__init__(parent, *args, **kwargs)
        self.set_halign(Gtk.Align.CENTER)
        self.attach(self.grid, 0, 2, 2, 1)

    def setup(self):
        content = None
        set_time_to_header = False
        for line, data in enumerate(self.FIELDS, start=1):
            header = Gtk.Label(label='')
            label_name = data.get('label_name')
            if 'mapping' in data:
                data = data.get('mapping', {}).get(content, {})
                set_time_to_header = True

            if 'header' not in data and not set_time_to_header:
                logger.error(f'Mapping not found for {content}: {data}')
                continue

            header.set_markup(f"<b>{data.get('header', '')}</b>")
            header.set_halign(Gtk.Align.START)

            if set_time_to_header:
                set_time_to_header = False
                self.time_to_header = header
            self.grid.attach(header, self.HEADER, line, 2, 1)

            content = _('Unknown')
            label = Gtk.Label(label=content)
            label.set_halign(Gtk.Align.START)
            self.content[label_name] = label
            self.grid.attach(label, self.CONTENT, line, 2, 1)
        GLib.timeout_add_seconds(2, self._update_labels)

    @staticmethod
    def get_battery_data():
        code, battery_raw = subprocess.getstatusoutput(
            "upower -i `upower -e | grep 'BAT'`"
        )
        battery_data = {}
        for line in battery_raw.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                battery_data[key.strip()] = value.strip()
        return code, battery_data

    def _update_labels(self, *args, **kwargs):
        code, battery_data = self.get_battery_data()
        for field, bat_field in self.UPDATE_FIELDS:
            self.content[field].set_label(battery_data.get(bat_field))

        data = self.TIME_TO_MAPPING.get(battery_data.get('state'), {})
        if self.time_to_header and data.get('header'):
            self.time_to_header.set_markup(f"<b>{data.get('header', '')}</b>")
        if data.get('filter') in ['time to empty', 'time to full']:
            content = battery_data.get(data.get('filter'))
            if content:
                time_to = content.split()
                if time_to[1] == 'hours':
                    content = f"{time_to[0]}{_(' hours')}"
                else:
                    content = f"{time_to[0]}{_(' min')}"
                self.content['time_to'].set_label(content)
        return True

    def complete_values(self):
        content = None
        code, battery_data = self.get_battery_data()

        for data in self.FIELDS:
            label_name = data.get('label_name')
            if not (label_name and label_name in self.content):
                continue
            if 'mapping' in data:
                data = data.get('mapping', {}).get(content, {})
                if self.time_to_header:
                    self.time_to_header.set_markup(f"<b>{data.get('header', '')}</b>")

            content = _('Unknown')
            if 'filter' in data:
                if code == 0:
                    content = battery_data.get(data.get('filter'))
                    if data.get('filter') in ['time to empty', 'time to full']:
                        time_to = content.split()
                        if time_to[1] == 'hours':
                            content = f"{time_to[0]}{_(' hours')}"
                        else:
                            content = f"{time_to[0]}{_(' min')}"
            elif 'text' in data:
                content = data.get('text')

            label = self.content[label_name]
            label.set_label(content)

class GeneralGrid(BasePageGrid):
    tab_name = _('General')
    allow_minimize = True
    HEADER = 1
    CONTENT = 3

    AC_MODE = 'AC'
    BAT_MODE = 'BAT'

    MIN_RESOLUTION = 50
    NORMAL_RESOLUTION = 100

    FIELDS = [
        {
            'label_name': 'application_on',
            'label': _('Application On - Off:'),
            'type': 'switch',
        },
        {
            'label_name': 'autostart',
            'label': _('Autostart application:'),
            'type': 'switch',
        },
        {
            'label_name': 'icono',
            'label': _('Icon on the taskbar (require restart app):'),
            'type': 'switch',
            'help': _('Note: If you have the autostart activated and the icon hide, '
                      'the app will be executed with the icon hide (once you restart the system)'),
        },
        {
            'label_name': 'working_failure',
            'label': _('Working mode in case of battery failure:'),
            'type': 'list',
            'list': [(0, AC_MODE), (1, BAT_MODE)],
        },
        {
            'label_name': 'plug_warn',
            'label': _('Remember to disconnect charger:'),
            'type': 'switch',
            'help': _('Note: It is very important not to use your laptop always connected to AC, '
                      'this option will notify you to disconnect charger if you stay 15 days connected. '
                      'You should complete a charge cycle.'),
        },
    ]
    MODES = [
        {
            'name': 'saving',
            'icon': 'normal.png',
            'label': _('Energy Saving'),
            'value': '1',
        },
        {
            'name': 'balanced',
            'icon': 'balanced_normal.png',
            'label': _('Balanced'),
            'value': '2',
        },
        {
            'name': 'performance',
            'icon': 'performance_normal.png',
            'label': _('Maximum Performance'),
            'value': '3',
        },
    ]

    def __init__(self, parent, *args, **kwargs):
        self.autostart_initial = None
        self.work_mode = None
        super(GeneralGrid, self).__init__(parent, *args, **kwargs)
        self.set_name('general')
        if self.parent.min_resolution:
            self.grid.set_name('smaller_label')
        else:
            self.grid.set_name('normal_label')
            self.grid.set_vexpand(True)
            self.grid.set_valign(Gtk.Align.CENTER)

        self.attach(self.grid, 0, 0, 1, 1)

    def setup(self):
        row = 0
        for row, data in enumerate(self.FIELDS, start=0):
            label = Gtk.Label(label=data.get('label'))
            if 'help' in data:
                field = Gtk.HBox(spacing=5)
                field.pack_start(label, True, True, 0)

                icon = Gtk.Image()
                icon.set_from_file(os.path.join(IMAGES_PATH, 'help.png'))
                icon.set_tooltip_text(data.get('help'))
                field.pack_start(icon, True, True, 0)
            else:
                field = label

            field.set_halign(Gtk.Align.START)
            self.grid.attach(field, self.HEADER, row, 2, 1)

            button = None
            button_type = data.get('type')
            if button_type == 'switch':
                button = Gtk.Switch()
                button.connect('notify::active', self.manage_events)
            elif button_type == 'list':
                store = Gtk.ListStore(int, str)
                for item in data.get('list', []):
                    store.append(item)
                button = Gtk.ComboBox.new_with_model_and_entry(store)
                button.set_entry_text_column(1)

            button.set_name(data.get('label_name'))
            button.set_halign(Gtk.Align.END)
            self.content[data.get('label_name')] = button

            self.grid.attach(button, self.CONTENT, row, 1, 1)

        if tdp_controller:
            row += 1
            if not config.has_option('TDP', 'tdpcontroller'):
                config.set('TDP', 'tdpcontroller', tdp_controller)

            label = Gtk.Label(label=_('Synchronice battery mode with CPU TDP mode:'))
            label.set_halign(Gtk.Align.START)
            self.grid.attach(label, self.HEADER, row, 2, 1)

            button = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
            button.set_name('saving_tdpsync')
            button.connect('notify::active', self.manage_events)
            self.content['saving_tdpsync'] = button
            self.grid.attach(button, self.CONTENT, row, 1, 1)

            code, msg = subprocess.getstatusoutput(f'which {tdp_controller}')
            if code != 0:
                logger.error('TDP Controller not installed')
                button.set_sensitive(False)
                button.set_state(False)

                if tdp_controller == 'slimbookintelcontroller':
                    link = INTEL_ES if lang == 'es' else INTEL_EN
                else:
                    link = AMD_ES if lang == 'es' else AMD_EN
                if link:
                    row += 1
                    label = Gtk.Label()
                    label.set_markup("<a href='{link}'>{text}</a>".format(
                        link=link,
                        text=_('Learn more about TDP Controller')
                    ))
                    label.set_name('link')
                    label.set_halign(Gtk.Align.START)
                    self.grid.attach(label, self.HEADER, row, 2, 1)

        row += 1
        buttons_grid = Gtk.Grid(column_homogeneous=True,
                                column_spacing=30,
                                row_spacing=20)
        buttons_grid.set_halign(Gtk.Align.CENTER)
        buttons_grid.set_name('radio_grid')
        self.grid.attach(buttons_grid, 0, row, 5, 3)

        label = Gtk.Label(label=_('Actual energy mode:').upper())
        label.set_name('modes')
        buttons_grid.attach(label, 0, 0, 3, 1)

        height = self.NORMAL_RESOLUTION
        width = self.NORMAL_RESOLUTION
        if self.parent.min_resolution:
            height = self.MIN_RESOLUTION
            width = self.MIN_RESOLUTION

        base_toggle = None
        for column, data in enumerate(self.MODES):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(IMAGES_PATH, data.get('icon')),
                width=width,
                height=height,
                preserve_aspect_ratio=True)
            img = Gtk.Image.new_from_pixbuf(pixbuf)
            img.set_halign(Gtk.Align.CENTER)
            img.set_valign(Gtk.Align.START)
            buttons_grid.attach(img, column, 1, 1, 1)

            toggle = Gtk.RadioButton.new_with_label_from_widget(base_toggle, data.get('label'))
            toggle.set_halign(Gtk.Align.CENTER)
            toggle.set_name(data.get('name'))
            toggle.connect('toggled', self.manage_events, data.get('value'))
            buttons_grid.attach(toggle, column, 2, 1, 1)
            if not base_toggle:
                base_toggle = toggle
            self.content[f"modo_actual_{data.get('value')}"] = toggle

    def complete_values(self):
        for field in ['saving_tdpsync']:
            button = self.content[field]
            button.set_active(config.getboolean('TDP', field))

        for field in ['application_on', 'icono', 'plug_warn']:
            button = self.content[field]
            button.set_active(config.getboolean('CONFIGURATION', field))

        self.autostart_initial = os.path.isfile(os.path.join(
            HOMEDIR, ".config/autostart/slimbookbattery-autostart.desktop"
        ))
        button = self.content['autostart']
        button.set_active(self.autostart_initial)

        content = pathlib.Path(TLP_CONF).read_text()
        if 'TLP_DEFAULT_MODE=AC' in content:
            self.content['working_failure'].set_active(0)
            self.work_mode = self.AC_MODE
        elif 'TLP_DEFAULT_MODE=BAT' in content:
            self.content['working_failure'].set_active(1)
            self.work_mode = self.BAT_MODE
        else:
            logger.error('WorkMode: Not found')

        current_mode = config.get('CONFIGURATION', 'modo_actual')
        button = self.content[f'modo_actual_{current_mode}']
        button.set_active(True)

    def manage_events(self, button, *args):
        name = button.get_name()

        if name in ['saving_tdpsync']:
            config.set('TDP', name, '1' if button.get_active() else '0')

        elif name in ['application_on', 'icono', 'plug_warn']:
            config.set('CONFIGURATION', name, '1' if button.get_active() else '0')

        elif name == 'autostart':
            self.autostart_initial = button.get_active()

        elif args:
            config.set('CONFIGURATION', 'modo_actual', args[0])

    def save_selection(self):

        # Default working mode
        button = self.content.get('working_failure')
        active = button.get_active_iter()

        if active is not None:
            model = button.get_model()
            work_mode = model[active][1]

            if work_mode and work_mode != self.work_mode:
                logger.info(f'Setting workmode {work_mode} ...')
                self.work_mode = work_mode

                code, msg = subprocess.getstatusoutput(f'pkexec slimbookbattery-pkexec change_config TLP_DEFAULT_MODE {work_mode}')

                if code != 0:
                    logger.error(msg)

        # Enables autostart
        if self.autostart_initial:
            destination = os.path.join(
                HOMEDIR, '.config/autostart'
            )

            if not os.path.isdir(destination):
                os.mkdir(destination)

            source = os.path.join(
                CURRENT_PATH, 'configuration', 'slimbookbattery-autostart.desktop'
            )

            if not os.path.isfile(os.path.join(destination, 'slimbookbattery-autostart.desktop')):
                logger.info('Enabling autostart ...')
                shutil.copy(source, destination)
                config.set('CONFIGURATION', 'autostart', '1')

        # Disables autostart
        else:
            logger.info('Disabling autostart ...')
            autostart_path = os.path.join(HOMEDIR, '.config/autostart/slimbookbattery-autostart.desktop')

            if os.path.isfile(autostart_path):
                os.remove(autostart_path)

            config.set('CONFIGURATION', 'autostart', '0')

class SettingsGrid(BasePageGrid):
    GRID_KWARGS = {
        'column_homogeneous': True,
        'row_homogeneous': False,
        'column_spacing': 25,
        'row_spacing': 20,
        'halign': Gtk.Align.CENTER,
    }

    INTEL_GOV = [
        (1, 'powersave'),
        (2, 'performance'),
    ]
    CPUFREQ_GOV = [
        (1, 'ondemand'),
        (2, 'schedutil'),
        (3, 'powersave'),
        (4, 'performance'),
        (5, 'conservative'),
    ]

    SECTION_MAPPING = {
        'ahorrodeenergia': {
            'limit_cpu': 'limit_cpu_ahorro',
            'governor': '',
            'graphic': 'graphics_ahorro',
            'sound': '',
            'wifi_profile': '',
            'bluetooth_disabled': '',
            'wifi_disabled': '',
            'brightness': 'ahorro_brightness',
            'brightness_switch': 'saving_brightness_switch',
            'animations': 'ahorro_animations',
            'bluetooth_os': '',
            'wifi_os': '',
            'wifi_lan': '',
            'usb': '',
            'usb_list': '',
            'bluetooth_blacklist': '',
            'printer_blacklist': '',
            'ethernet_blacklist': '',
            'usb_shutdown': '',
        },
        'equilibrado': {
            'limit_cpu': 'limit_cpu_equilibrado',
            'governor': '',
            'graphic': 'graphics_equilibrado',
            'sound': '',
            'wifi_profile': '',
            'bluetooth_disabled': '',
            'wifi_disabled': '',
            'brightness': 'equilibrado_brightness',
            'brightness_switch': 'balanced_brightness_switch',
            'animations': 'equilibrado_animations',
            'bluetooth_os': '',
            'wifi_os': '',
            'wifi_lan': '',
            'usb': '',
            'usb_list': '',
            'bluetooth_blacklist': '',
            'printer_blacklist': '',
            'ethernet_blacklist': '',
            'usb_shutdown': '',
        },
        'maximorendimiento': {
            'limit_cpu': 'limit_cpu_maximorendimiento',
            'governor': '',
            'graphic': 'graphics_maxrendimiento',
            'sound': '',
            'wifi_profile': '',
            'bluetooth_disabled': '',
            'wifi_disabled': '',
            'brightness': 'maxrendimiento_brightness',
            'brightness_switch': 'power_brightness_switch',
            'animations': 'maxrendimiento_animations',
            'bluetooth_os': '',
            'wifi_os': '',
            'wifi_lan': '',
            'usb': '',
            'usb_list': '',
            'bluetooth_blacklist': '',
            'printer_blacklist': '',
            'ethernet_blacklist': '',
            'usb_shutdown': '',
        },
    }

    BATTERY_FIELDS = [
        {
            'name': 'limit_cpu',
            'label': _('Limit CPU profile:'),
            'type': 'list',
            'icon': 'warning.png',
            'help': _('Note: this setting affects to performance'),
            'list': [
                (1, _('maximum')),
                (2, _('medium')),
                (3, _('none')),
            ],
        },
        {
            'name': 'governor',
            'label': _('CPU scaling governor saving profile:'),
            'type': 'governor',
            'intel_pstate': INTEL_GOV,
            'amd-pstate': CPUFREQ_GOV,
            'acpi-cpufreq': CPUFREQ_GOV,
            'intel_cpufreq': CPUFREQ_GOV,
        },
        {
            'name': 'graphic',
            'label': _('Graphic card saving profile (Nvidia-AMD-Intel):'),
            'type': 'switch',
        },
        {
            'name': 'sound',
            'label': _('Sound power saving profile:'),
            'type': 'switch',
            'help': _('Note: this setting can cause slight clicks in sound output'),
        },
        {
            'name': 'wifi_profile',
            'label': _('Wi-Fi power saving profile:'),
            'type': 'switch',
            'help': _('Note: power save can cause an unstable wifi connection.') + ' ' + _('Disabled in tlp version <1.3.'),
        },
        {
            'name': 'bluetooth_disabled',
            'label': _('Bluetooth disabled when not in use:'),
            'type': 'switch',
        },
        {
            'name': 'wifi_disabled',
            'label': _('Wi-Fi disabled when not in use:'),
            'type': 'switch',
        },
    ]

    PERSIST_FIELDS = [
        {
            'name': 'brightness',
            'label': _('Set screen brightness:'),
            'type': 'scale',
            'help': _('Note: this option reduces the battery consumption considerably'),
        },
        {
            'name': 'animations',
            'label': _('Disable animations:'),
            'type': 'animations',
        },
        {
            'name': 'bluetooth_os',
            'label': _('Bluetooth does not boot on start:'),
            'type': 'switch',
        },
        {
            'name': 'wifi_os',
            'label': _('Wi-Fi does not boot on start:'),
            'type': 'switch',
        },
        {
            'name': 'wifi_lan',
            'label': _('Disable Wi-Fi when LAN is connected:'),
            'type': 'switch',
        },
        {
            'name': 'usb',
            'label': _('Autosuspend USB Ports:'),
            'type': 'switch',
            'help': _('Note: Set autosuspend mode for all USB devices upon system start or a change of power source. '
                      'Input devices like mice and keyboards as well as scanners are excluded by default')
        },
        {
            'name': 'usb_list',
            'label': _('Excluded USB IDs from USB autosuspend:'),
            'type': 'usb',
            'help': _('Note: You need to write in the Text Box the USB IDs '
                      '(separate with spaces) to exclude from autosuspend')
        },
        {
            'name': 'bluetooth_blacklist',
            'label': _('Exclude bluetooth devices from USB autosuspend:'),
            'type': 'switch',
        },
        {
            'name': 'printer_blacklist',
            'label': _('Exclude printer devices from USB autosuspend:'),
            'type': 'switch',
        },
        {
            'name': 'ethernet_blacklist',
            'label': _('Exclude Ethernet devices from USB autosuspend:'),
            'type': 'switch',
        },
        {
            'name': 'usb_shutdown',
            'label': _('Disable USB autosuspend mode upon system shutdown:'),
            'type': 'switch',
        },
    ]

    CPU_LIMIT = {
        1: {
            'CPU_MIN_PERF_ON_AC': 0,
            'CPU_MAX_PERF_ON_AC': 100,
            'CPU_MIN_PERF_ON_BAT': 0,
            'CPU_MAX_PERF_ON_BAT': 33,
            'CPU_BOOST_ON_AC': 1,
            'CPU_BOOST_ON_BAT': 0,
            'CPU_ENERGY_PERF_POLICY_ON_AC': 'balance_performance',
            'CPU_ENERGY_PERF_POLICY_ON_BAT': 'power',
            'SCHED_POWERSAVE_ON_AC': 0,
            'SCHED_POWERSAVE_ON_BAT': 0,
        },
        2: {
            'CPU_MIN_PERF_ON_AC': 0,
            'CPU_MAX_PERF_ON_AC': 100,
            'CPU_MIN_PERF_ON_BAT': 0,
            'CPU_MAX_PERF_ON_BAT': 80,
            'CPU_BOOST_ON_AC': 1,
            'CPU_BOOST_ON_BAT': 0,
            'CPU_ENERGY_PERF_POLICY_ON_AC': 'balance_performance',
            'CPU_ENERGY_PERF_POLICY_ON_BAT': 'power',
            'SCHED_POWERSAVE_ON_AC': 0,
            'SCHED_POWERSAVE_ON_BAT': 0,
        },
        3: {
            'CPU_MIN_PERF_ON_AC': 0,
            'CPU_MAX_PERF_ON_AC': 100,
            'CPU_MIN_PERF_ON_BAT': 0,
            'CPU_MAX_PERF_ON_BAT': 100,
            'CPU_BOOST_ON_AC': 1,
            'CPU_BOOST_ON_BAT': 1,
            'CPU_ENERGY_PERF_POLICY_ON_AC': 'balance_performance',
            'CPU_ENERGY_PERF_POLICY_ON_BAT': 'balance_performance',
            'SCHED_POWERSAVE_ON_AC': 0,
            'SCHED_POWERSAVE_ON_BAT': 0,
        },
    }

    @staticmethod
    def get_governor():
        governors = subprocess.getoutput(
            'for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_driver; do cat $i; done'
        ).split('\n')
        governor_driver = None

        for governor_driver in governors:
            if governor_driver not in ['intel_pstate', 'acpi-cpufreq', 'intel_cpufreq', 'amd-pstate']:
                governor_driver = None
                break

        return governor_driver

    @staticmethod
    def get_usb_list():
        USB_ID_REGEX = re.compile('ID ([a-f0-9]{4}:[a-f0-9]{4})')
        usb_list = {}
        lsusb_lines = subprocess.getoutput('lsusb').split('\n')
        for line in lsusb_lines:
            match = USB_ID_REGEX.search(line)
            if match:
                usb_id = match.groups()[0]
                usb_list[usb_id] = line[line.find('ID'):]
        return usb_list

    def __init__(self, parent, custom_file, *args, **kwargs):
        self.custom_file = custom_file
        self.custom_file_path = os.path.join(HOMEDIR, '.config/slimbookbattery/custom', custom_file)

        self.label_col = 0
        self.button_col = 3
        self.label_col2 = 4
        self.button_col2 = 8

        if parent.min_resolution:
            self.button_col = 5
            self.label_col2 = 0
            self.button_col2 = 5

        super(SettingsGrid, self).__init__(parent, *args, **kwargs)
        if self.parent.min_resolution:
            self.grid.set_name('smaller_label')
        self.attach(self.grid, 0, 0, 2, 1)

    def setup(self):
        row = self.setup_battery_column()
        row = row + 1 if self.parent.min_resolution else 1
        self.setup_persist_column(row)

    def setup_fields(self, start, fields, label_col, button_col):
        row_correction = 0
        row = start
        for row, data in enumerate(fields, start=start):
            button_type = data.get('type')
            col_correction = 0
            if button_type == 'governor':
                button_type = 'list'
                data['list'] = data.get(self.get_governor(), [])
                if not data['list']:
                    row_correction += 1
                    continue
            elif button_type == 'animations':
                if 'gnome' not in os.environ.get('XDG_CURRENT_DESKTOP', '').lower():
                    row_correction += 1
                    continue
                button_type = 'switch'
            elif button_type == 'usb':
                help_msg = data.get('help')
                usb_list = self.get_usb_list()
                data['help'] = '{}.\n\n{}'.format(
                    help_msg,
                    '\n'.join(usb_list.values())
                )

            label = Gtk.Label(label=data.get('label'))
            label.set_halign(Gtk.Align.START)
            if 'help' in data:
                table_icon = Gtk.Table(n_columns=2, n_rows=1, homogeneous=False)
                table_icon.set_valign(Gtk.Align.END)
                table_icon.attach(label, 0, 1, 0, 1,
                                  xpadding=0,
                                  ypadding=5,
                                  xoptions=Gtk.AttachOptions.SHRINK,
                                  yoptions=Gtk.AttachOptions.SHRINK)
                icon = Gtk.Image()
                icon.set_from_file(os.path.join(IMAGES_PATH, data.get('icon', 'help.png')))
                icon.set_tooltip_text(data.get('help'))
                icon.set_halign(Gtk.Align.START)
                table_icon.attach(icon, 1, 2, 0, 1,
                                  xpadding=10,
                                  ypadding=5,
                                  xoptions=Gtk.AttachOptions.SHRINK,
                                  yoptions=Gtk.AttachOptions.SHRINK)
                self.grid.attach(table_icon, label_col, row - row_correction, 4, 1)
            else:
                self.grid.attach(label, label_col, row - row_correction, 4, 1)

            button = None
            top = 1
            if button_type == 'usb':
                button = Gtk.Entry(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                col_correction = 1
                top = 2

            elif button_type == 'switch':
                button = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
                button.connect('notify::active', self.manage_events)

            elif button_type == 'scale':
                button = Gtk.Scale()
                button.set_adjustment(Gtk.Adjustment.new(0, 0, 100, 5, 5, 0))
                button.set_digits(0)
                button.set_hexpand(True)
                button.connect('button-release-event', self.manage_events)

                button_on_off = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.END)
                name = f"{data.get('name')}_switch"
                button_on_off.set_name(name)
                button_on_off.connect('notify::active', self.manage_events)
                self.content[name] = button_on_off
                self.grid.attach(button_on_off, button_col - col_correction, row, 1, 1)
                top = 2
                col_correction = 2
            elif button_type == 'list':
                top = 2
                store = Gtk.ListStore(int, str)
                for item in data.get('list', []):
                    store.append(item)
                button = Gtk.ComboBox.new_with_model_and_entry(store)
                if len(data.get('list', [])) == 1:
                    button.set_active(0)
                    button.set_sensitive(False)
                button.set_valign(Gtk.Align.CENTER)
                button.set_halign(Gtk.Align.END)
                button.connect('changed', self.manage_events)
                button.set_entry_text_column(1)
                col_correction = 1

            button.set_name(data.get('name'))
            self.content[data.get('name')] = button
            self.grid.attach(button, button_col - col_correction, row - row_correction, top, 1)
        return row

    def setup_battery_column(self):
        title = Gtk.Label(label='')
        title.set_markup(
            '<big><b>' + (_('Battery mode parameters (disabled when you connect AC power):')) + '</b></big>')
        title.set_halign(Gtk.Align.START)
        self.grid.attach(title, self.label_col, 1, 4, 1)
        row = self.setup_fields(2, self.BATTERY_FIELDS, self.label_col, self.button_col)
        return row

    def setup_persist_column(self, row):
        title = Gtk.Label(label='')
        title.set_markup('<big><b>' + (_('Persistent changes:')) + '</b></big>')
        if self.parent.min_resolution:
            title.set_name('title')
        title.set_halign(Gtk.Align.START)
        self.grid.attach(title, self.label_col2, row, 5, 1)
        row += 1
        self.setup_fields(row, self.PERSIST_FIELDS, self.label_col2, self.button_col2)

    def complete_values(self):
        button = self.content['limit_cpu']
        value = config.getint('SETTINGS', self.SECTION_MAPPING[self.custom_file]['limit_cpu'])
        button.set_active(value - 1)

        button = self.content['brightness']
        button.set_value(
            config.getint(
                'SETTINGS',
                self.SECTION_MAPPING[self.custom_file]['brightness']
            )
        )
        for switch in ['graphic', 'brightness_switch', 'animations']:
            if switch not in self.content:
                continue
            button = self.content[switch]
            button.set_active(
                config.getboolean(
                    'SETTINGS',
                    self.SECTION_MAPPING[self.custom_file][switch]
                )
            )

        content = pathlib.Path(self.custom_file_path).read_text()
        for key, search in {
            'sound': 'SOUND_POWER_SAVE_ON_BAT=1',
            'wifi_profile': 'WIFI_PWR_ON_BAT=on',
            'bluetooth_blacklist': 'USB_BLACKLIST_BTUSB=1 & USB_DENYLIST_BTUSB=1',
            'printer_blacklist': 'USB_BLACKLIST_PRINTER=1 & USB_DENYLIST_PRINTER=1',
            'ethernet_blacklist': 'USB_BLACKLIST_WWAN=1 & USB_DENYLIST_WWAN=1',
            'usb_shutdown': 'USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=1',
        }.items():

            button = self.content[key]

            if len(search.split(' & ')) > 1:
                search = search.split(' & ')
                active = all(variable in content for variable in search)
                button.set_active(active)
            else:
                button.set_active(search in content)

        for key, search in {
            'disabled': 'DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE',
            'os': 'DEVICES_TO_DISABLE_ON_STARTUP',
        }.items():
            line = content[content.find(search):]
            line = line[:line.find('\n')]
            button_bluetooth = self.content[f'bluetooth_{key}']
            button_bluetooth.set_active('bluetooth' in line)
            button_wifi = self.content[f'wifi_{key}']
            button_wifi.set_active('wifi' in line)

        button = self.content['governor']
        governor = self.get_governor()
        line = content[content.find('CPU_SCALING_GOVERNOR_ON_BAT='):]
        line = line[:line.find('\n')]
        gov_mode = line[line.find('=') + 1:]
        active_mode = None
        if governor == 'intel_pstate':
            values = list(dict(self.INTEL_GOV).values())
            if gov_mode in values:
                active_mode = values.index(gov_mode)
            # Setting default mode to save energy
            elif self.custom_file == 'ahorrodeenergia':
                active_mode = values.index('powersave')
            else:
                active_mode = values.index('performance')
        elif governor in ['acpi-cpufreq', 'intel_cpufreq', 'amd-pstate']:
            values = list(dict(self.CPUFREQ_GOV).values())
            if gov_mode in values:
                active_mode = values.index(gov_mode)
            # Setting default mode
            elif self.custom_file == 'ahorrodeenergia':
                active_mode = values.index('powersave')
            else:
                active_mode = values.index('ondemand')

        if active_mode is not None:
            button.set_active(active_mode)

        button = self.content['wifi_lan']

        lan_disconnect = content[content.find('DEVICES_TO_ENABLE_ON_LAN_DISCONNECT='):]
        lan_disconnect = lan_disconnect[:lan_disconnect.find('\n')]

        lan_connect = content[content.find('DEVICES_TO_DISABLE_ON_LAN_CONNECT='):]
        lan_connect = lan_connect[:lan_connect.find('\n')]

        button.set_active(
            'wifi' in lan_disconnect and 'wifi' in lan_connect
        )

        button = self.content['usb']
        usb_autosuspend = 'USB_AUTOSUSPEND=1' in content
        button.set_active(usb_autosuspend)

        button = self.content['usb_list']
        button.set_sensitive(usb_autosuspend)
        usb_blacklist = content[content.find('USB_BLACKLIST'):]
        usb_blacklist = usb_blacklist[usb_blacklist.find('=') + 1:usb_blacklist.find('\n')]
        usb_blacklist = usb_blacklist.replace('"', '')

        button.set_text(usb_blacklist)

    def manage_events(self, button, *args):
        name = button.get_name()
        option = self.SECTION_MAPPING[self.custom_file][name]
        if option:
            if name in ['graphic', 'brightness_switch', 'animations']:
                config.set(
                    'SETTINGS', option,
                    '1' if button.get_active() else '0'
                )
            elif name == 'brightness':
                config.set(
                    'SETTINGS', option,
                    str(int(button.get_value()))
                )
            elif name == 'limit_cpu':
                active = button.get_active_iter()
                if active is not None:
                    model = button.get_model()
                    work_mode = model[active][0]
                    config.set('SETTINGS', option, str(work_mode))

        if name == 'brightness_switch':
            self.content['brightness'].set_sensitive(button.get_active())
        elif name == 'usb':
            for field in [
                'usb_list',
                'bluetooth_blacklist', 'printer_blacklist',
                'ethernet_blacklist', 'usb_shutdown',
            ]:
                self.content[field].set_sensitive(button.get_active())

    def save_selection(self):
        content = pathlib.Path(self.custom_file_path).read_text()
        base_cmd = 'sed -i "/{search}=/ c{search}={value}" {file}'

        button = self.content['governor']
        active = button.get_active_iter()
        if active is not None:
            search = 'CPU_SCALING_GOVERNOR_ON_BAT'
            model = button.get_model()
            value = model[active][1]
            if '{search}={value}'.format(search=search, value=value) not in content:
                cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
                code, msg = subprocess.getstatusoutput(cmd)
                logger.info(f'[{self.custom_file}] Setting {search} saving to "{value}" --> Exit({code}): {msg}')

        value = config.getint('SETTINGS', self.SECTION_MAPPING[self.custom_file]['limit_cpu'])
        for search, value in self.CPU_LIMIT[value].items():
            if '{search}={value}'.format(search=search, value=value) not in content:
                cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
                code, msg = subprocess.getstatusoutput(cmd)
                logger.info(f'[{self.custom_file}] Setting {search} saving to "{value}" --> Exit({code}): {msg}')

        for key, search_items in {
            'sound': 'SOUND_POWER_SAVE_ON_BAT',
            'bluetooth_blacklist': 'USB_BLACKLIST_BTUSB USB_DENYLIST_BTUSB',
            'printer_blacklist': 'USB_BLACKLIST_PRINTER USB_DENYLIST_PRINTER',
            'ethernet_blacklist': 'USB_BLACKLIST_WWAN USB_DENYLIST_WWAN',
            'usb_shutdown': 'USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN',
            'wifi_profile': 'WIFI_PWR_ON_BAT',
            'usb': 'USB_AUTOSUSPEND',
        }.items():

            button = self.content[key]
            if search_items == 'WIFI_PWR_ON_BAT':
                value = 'on' if button.get_active() and TLP_CONF != '/etc/default/tlp' else 'off'
            else:
                value = '1' if button.get_active() else '0'

            for search in search_items.split(' '):
                # print('{}'.format(Colors.RED)+search+'{}'.format(Colors.ENDC))
                if '{search}={value}'.format(search=search, value=value) not in content:
                    # print('{}Not in content{}'.format(Colors.GREEN, Colors.ENDC))
                    if search in content:
                        cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
                        code, msg = subprocess.getstatusoutput(cmd)
                        logger.info(f'[{self.custom_file}] Setting {search} saving to "{value}" --> Exit({code}): {msg}')

        for key, search in {
            'disabled': 'DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE',
            'os': 'DEVICES_TO_DISABLE_ON_STARTUP',
        }.items():
            value = []
            button_bluetooth = self.content[f'bluetooth_{key}']
            if button_bluetooth.get_active():
                value.append('bluetooth')
            button_wifi = self.content[f'wifi_{key}']
            if button_wifi.get_active():
                value.append('wifi')
            value = ' '.join(value)
            cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
            code, msg = subprocess.getstatusoutput(cmd)
            logger.info(f'[{self.custom_file}] Setting {search} saving to "{value}" --> Exit({code}): {msg}')

        button = self.content['wifi_lan']
        value = 'wifi' if button.get_active() else ''
        for search in ['DEVICES_TO_DISABLE_ON_LAN_CONNECT', 'DEVICES_TO_ENABLE_ON_LAN_DISCONNECT']:
            cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
            code, msg = subprocess.getstatusoutput(cmd)
            logger.info(f'[{self.custom_file}] Setting {search} saving to "{value}" --> Exit({code}): {msg}')

        button = self.content['usb_list']
        for key, search in {
            'old_usb_list': 'USB_BLACKLIST',
            'new_usb_list': 'USB_DENYLIST',
        }.items():
            value = button.get_text()
            if '{search}={value}'.format(search=search, value=value) not in content:
                if search in content:
                    cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
                    code, msg = subprocess.getstatusoutput(cmd)
                    logger.info(f'[{self.custom_file}] Setting {search} saving to "{value}" --> Exit({code}): {msg}')


class CyclesGrid(BasePageGrid):
    tab_name = _('Cycles')
    GRID_KWARGS = {
        'column_homogeneous': True,
        'column_spacing': 40,
        'row_spacing': 20,
        'halign': Gtk.Align.CENTER,
    }
    FIELDS = [
        {
            'label_name': 'alerts',
            'label': _('Enable cycle alerts'),
            'type': 'switch',
            'lenght': 10
        },
        {
            'label_name': 'max_battery_value',
            'label': _('Max battery value:'),
            'type': 'scale',
            'lenght': 100
        },
        {
            'label_name': 'min_battery_value',
            'label': _('Min battery value:'),
            'type': 'scale',
            'lenght': 100
        },
        {
            'label_name': 'max_battery_times',
            'label': _('Number of times:'),
            'type': 'scale',
            'lenght': 10
        },
        {
            'label_name': 'time_between_warnings',
            'label': _('Time between Warnings:'),
            'type': 'scale',
            'lenght': 100
        },
    ]

    def setup(self):
        for row, data in enumerate(self.FIELDS):
            button_type = data.get('type')

            label = Gtk.Label(label=data.get('label'))
            label.set_halign(Gtk.Align.START)
            self.grid.attach(label, 0, row, 1, 1)

            button = None
            if button_type == 'switch':
                button = Gtk.Switch(halign=Gtk.Align.START)
                button.connect('notify::active', self.manage_events)
            elif button_type == 'scale':
                button = Gtk.Scale()
                button.set_size_request(200, 10)
                button.set_adjustment(Gtk.Adjustment.new(0, 0, data.get('lenght'), 5, 5, 0))
                button.set_digits(0)
                button.set_hexpand(True)
                button.connect('change-value', self.manage_events)

            button.set_name(data.get('label_name'))
            self.content[data.get('label_name')] = button
            self.grid.attach(button, 1, row, 1, 1)
        self.attach(self.grid, 0, 3, 2, 1)

    def complete_values(self):
        for data in self.FIELDS:
            name = data.get('label_name')
            button_type = data.get('type')
            button = self.content[name]
            if button_type == 'switch':
                button.set_active(config.getboolean('CONFIGURATION', name))
            elif button_type == 'scale':
                button.set_value(config.getint('CONFIGURATION', name))

    def manage_events(self, button, *args):
        name = button.get_name()
        if isinstance(button, Gtk.Switch):
            value = '1' if button.get_active() else '0'
        else:
            value = str(int(button.get_value()))
        config.set('CONFIGURATION', name, value)


class Preferences(Gtk.ApplicationWindow):
    CONFIG_TABS = [
        {
            'filename': 'ahorrodeenergia',
            'attr': 'low_page_grid',
            'title': _('Energy Saving'),
        },
        {
            'filename': 'equilibrado',
            'attr': 'mid_page_grid',
            'title': _('Balanced'),
        },
        {
            'filename': 'maximorendimiento',
            'attr': 'high_page_grid',
            'title': _('Maximum Performance'),
        },
    ]
    ANIMATIONS = {
        '1': 'ahorro_animations',
        '2': 'equilibrado_animations',
        '3': 'maxrendimiento_animations',
    }

    min_resolution = False

    def __init__(self):

        # Load updates if exist
        if os.path.isdir(UPDATES_DIR):
            logging.info('Loading updates ...')

            for file in os.listdir(UPDATES_DIR):

                process = os.path.join(UPDATES_DIR, file)
                proc = subprocess.Popen(f'bash {process}', shell=True)

                # Wait for child process to terminate. Returns returncode attribute.
                proc.wait()
                logger.info(f'\n{process} returned exit code {proc.returncode}.')

                if proc.returncode == 0:
                    try:
                        os.remove(process)
                    except:
                        logger.error('Could not remove update after completion.')

        self.__setup_css()
        Gtk.Window.__init__(self, title=(_('Slimbook Battery Preferences')))

        self.get_style_context().add_class("bg-image")
        self.set_position(Gtk.WindowPosition.CENTER)  # // Allow movement

        self.set_size_request(0, 0)

        if SESSION_TYPE and SESSION_TYPE == 'x11':
            self.set_decorated(False)
            self.set_draggable()
            self.set_name('decorated')
        else:
            self.set_decorated(True)

        self.set_resizable(False)

        splash = os.path.join(CURRENT_PATH, 'splash.py')
        self.child_process = subprocess.Popen(splash, stdout=subprocess.PIPE)

        self.general_page_grid = None
        self.low_page_grid = None
        self.mid_page_grid = None
        self.high_page_grid = None
        try:

            self.set_ui()
        except Exception:
            logger.exception('Unexpected error')
            os.system('pkexec slimbookbattery-pkexec restore')
            config.read(CONFIG_FILE)

            try:
                for children in self.get_children():
                    print(children)
                self.remove(children)
                self.set_ui()
            except Exception:
                logger.exception('Unexpected error')
                self.child_process.terminate()

        if VTE_VERSION[0] == 0:
            self.check_recommendations()

    def set_draggable(self):
        def on_realize(widget):
            monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
            scale = monitor.get_scale_factor()
            monitor_width = monitor.get_geometry().width / scale
            monitor_height = monitor.get_geometry().height / scale
            width = self.get_preferred_width()[0]
            height = self.get_preferred_height()[0]
            self.move((monitor_width - width) / 2, (monitor_height - height) / 2)

        def on_mouse_moved(widget, event):
            if self.is_in_drag:
                xi, yi = self.get_position()
                xf = int(xi + event.x_root - self.x_in_drag)
                yf = int(yi + event.y_root - self.y_in_drag)
                if math.sqrt(math.pow(xf - xi, 2) + math.pow(yf - yi, 2)) > 10:
                    self.x_in_drag = event.x_root
                    self.y_in_drag = event.y_root
                    self.move(xf, yf)

        def on_mouse_button_released(widget, event):
            if event.button == 1:
                self.is_in_drag = False
                self.x_in_drag = event.x_root
                self.y_in_drag = event.y_root

        def on_mouse_button_pressed(widget, event):
            if event.button == 1:
                self.is_in_drag = True
                self.x_in_drag, self.y_in_drag = self.get_position()
                self.x_in_drag = event.x_root
                self.y_in_drag = event.y_root

        # Movement
        self.is_in_drag = False
        self.x_in_drag = 0
        self.y_in_drag = 0
        self.connect('button-press-event', on_mouse_button_pressed)
        self.connect('button-release-event', on_mouse_button_released)
        self.connect('motion-notify-event', on_mouse_moved)
        # Center
        self.connect('realize', on_realize)  # On Wayland, monitor = None --> ERROR

    def set_ui(self):
        self.set_default_icon(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'normal.png'),
            width=825,
            height=225,
            preserve_aspect_ratio=True)
        )

        display_width, display_height = utils.get_display_resolution()
        if int(display_width) >= 1550 and int(display_height) >= 850:
            logger.debug(_('Full window is displayed'))
        else:
            self.resize(1100, 650)
            self.min_resolution = True

        win_grid = Gtk.Grid(column_homogeneous=True,
                            column_spacing=0,
                            row_spacing=10)

        self.add(win_grid)

        restore_values = Gtk.Button(label=(_('Restore default values')), valign=Gtk.Align.END, halign=Gtk.Align.END)
        restore_values.set_name('restore')
        restore_values.connect("clicked", self.manage_events)

        btn_cancel = Gtk.Button(label=(_('Cancel')), valign=Gtk.Align.END, halign=Gtk.Align.END)
        btn_cancel.set_name('cancel')
        btn_cancel.connect("clicked", self.manage_events, 'x')

        btn_accept = Gtk.Button(label=(_('Accept')), valign=Gtk.Align.END, halign=Gtk.Align.END)
        btn_accept.set_name('accept')
        btn_accept.connect("clicked", self.manage_events)

        label_version = Gtk.Label(label='', halign=Gtk.Align.START)
        label_version.set_name('version')

        desk_config = configparser.ConfigParser()
        # Try load system version
        desk_config.read('/usr/share/applications/slimbookbattery.desktop')
        # Overwrite system version with local one (For develop version)
        desk_config.read(os.path.join(CURRENT_PATH, '../slimbookbattery.desktop'))
        if desk_config.has_option('Desktop Entry', 'Version'):
            version = desk_config.get('Desktop Entry', 'Version')
        else:
            version = 'Unknown'
        label_version.set_markup(f'<span font="10">Version: {version}</span>')

        win_grid.attach(label_version, 0, 5, 1, 1)

        if not os.path.isfile(os.path.join(CONFIG_FOLDER, 'default/equilibrado')):
            logger.debug('Copy configuration files ...')
            base_folder = '/usr/share/slimbookbattery/'
            if not os.path.isdir(base_folder):
                base_folder = os.path.normpath(os.path.join(CURRENT_PATH, '..'))

            shutil.copytree(os.path.join(base_folder, 'custom'), os.path.join(CONFIG_FOLDER, 'custom'))
            shutil.copytree(os.path.join(base_folder, 'default'), os.path.join(CONFIG_FOLDER, 'default'))

        if self.min_resolution:
            height = 200
            width = 800
        else:
            height = 210
            width = 810

        if SESSION_TYPE and SESSION_TYPE == 'x11':
            pixbuff = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(IMAGES_PATH, 'slimbookbattery-header-4.png'),
                width=width,
                height=height,
                preserve_aspect_ratio=True
            )
            self.logo = Gtk.Image.new_from_pixbuf(pixbuff)

            self.logo.set_halign(Gtk.Align.START)
            self.logo.set_valign(Gtk.Align.START)
            win_grid.attach(self.logo, 0, 0, 4, 2)

            close_box = Gtk.HBox(halign=Gtk.Align.END, valign=Gtk.Align.START)

            close = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(IMAGES_PATH, 'cross.png'),
                width=20,
                height=20,
                preserve_aspect_ratio=True
            ))
            close.set_name('close_button')

            event_close_box = Gtk.EventBox()
            event_close_box.set_name('close_box')
            event_close_box.add(close)
            event_close_box.set_halign(Gtk.Align.END)
            event_close_box.set_valign(Gtk.Align.START)
            event_close_box.connect('button-press-event', self.manage_events)

            # close_box.add(check)
            close_box.add(event_close_box)
            win_grid.attach(close_box, 4, 0, 1, 4)

        check = Gtk.CheckButton.new_with_label(label=_('System style'))
        check.set_name('style')
        check.set_tooltip_text(_('Style will be changed once you reopen the preferences window.'))
        style = config.get('CONFIGURATION', 'style') if config.has_option('CONFIGURATION', 'style') else 'system'
        if style == 'system':
            check.set_active(True)

        check.connect('clicked', self.manage_events)

        buttons_box = Gtk.Box()
        buttons_box.pack_start(check, True, True, 0)
        buttons_box.pack_start(btn_cancel, True, True, 0)
        buttons_box.pack_start(restore_values, True, True, 0)
        buttons_box.pack_start(btn_accept, True, True, 0)
        buttons_box.set_halign(Gtk.Align.END)
        win_grid.attach(buttons_box, 2, 5, 3, 1)

        if self.min_resolution:
            buttons_box.set_name('smaller_label')

    # NOTEBOOK ***************************************************************

        notebook = Gtk.Notebook.new()
        if self.min_resolution:
            notebook.set_name('smaller_label')
            notebook.set_vexpand(True)
            notebook.set_hexpand(False)

        notebook.set_tab_pos(Gtk.PositionType.TOP)
        win_grid.attach(notebook, 0, 1, 5, 4)

        logger.debug(f"{_('Width: ')}{display_width} {_(' Height: ')}{display_height}")

        # CREATE TABS
        self.general_page_grid = GeneralGrid(self)
        self.general_page_grid.set_hexpand(True)
        notebook.append_page(self.general_page_grid.get_page(),
                             Gtk.Label.new(self.general_page_grid.tab_name))

        for data in self.CONFIG_TABS:
            setattr(
                self, data.get('attr'),
                SettingsGrid(self, data.get('filename'))
            )
            page_grid = getattr(self, data.get('attr'))
            notebook.append_page(page_grid.get_page(),
                                 Gtk.Label.new(data.get('title')))

        cycles_page_grid = CyclesGrid(self)
        notebook.append_page(cycles_page_grid.get_page(),
                             Gtk.Label.new(cycles_page_grid.tab_name))

        battery_page_grid = BatteryGrid(self)
        notebook.append_page(battery_page_grid.get_page(),
                             Gtk.Label.new(battery_page_grid.tab_name))

        info_page_grid = InfoPageGrid(self)
        notebook.append_page(info_page_grid.get_page(),
                             Gtk.Label.new(info_page_grid.tab_name))

        # END
        self.child_process.terminate()
        # SHOW
        self.show_all()

    # CLASS FUNCTIONS ***********************************

    def manage_events(self, button, *args):
        name = button.get_name()
        if name == 'style':
            value = 'system' if button.get_active() else 'original'
            logger.info(value)
            config.set('CONFIGURATION', 'style', value)

            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)

            height = 200
            width = 800

            # To do: restore css provider
            # self.hide()
            # self.__setup_css()
            # self.show_all()

        elif name == 'restore':
            os.system('pkexec slimbookbattery-pkexec restore')
            config.read(CONFIG_FILE)
            
            for children in self.get_children():
                print(children)
            self.remove(children)
            self.set_ui()
            # self.hide()

            # win = Preferences()
            # win.connect("destroy", Gtk.main_quit)
            # win.show_all()

        elif name == 'accept':
            self.apply_conf()

            # Remove updates dir
            if os.path.isdir(UPDATES_DIR):
                try:
                    os.rmdir(UPDATES_DIR)
                except:
                    logger.error('Updates folder not empty')

        if name in ['accept', 'close_box', 'cancel']:
            Gtk.main_quit()
            exit(0)

    def __setup_css(self):
        """Setup the CSS and load it."""
        style = 'original'
        if config.has_option('CONFIGURATION', 'style'):
            style = config.get('CONFIGURATION', 'style')

        provider_file = f'{CURRENT_PATH}/css/{style}-style.css'
        provider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        provider.load_from_path(provider_file)
        context.add_provider_for_screen(screen, provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        logger.debug(f"Loading CSS - {style}")

    def animations(self, mode):
        check_desktop = 'gnome' in os.environ.get("XDG_CURRENT_DESKTOP", '').lower()

        if check_desktop:
            logger.info(f'Setting mode {mode} animations')
            if mode == '0':  # Application off
                logger.info('Animations Active')
                os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')
            elif mode in self.ANIMATIONS:
                if config.getboolean('SETTINGS', self.ANIMATIONS.get(mode)):
                    logger.info('Animations Inactive')
                    os.system('dconf write /org/gnome/desktop/interface/enable-animations false')
                    os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch false')
                    os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch false')
                else:
                    logger.info('Animations Active')
                    os.system('dconf write /org/gnome/desktop/interface/enable-animations true')
                    os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-app-switch true')
                    os.system('dconf write /org/gnome/shell/extensions/dash-to-panel/animate-window-launch true')
            else:
                logger.info('mode not found')
        else:
            logger.info('Not Gnome desktop "{}"'.format(os.environ.get("XDG_CURRENT_DESKTOP", '')))

    def apply_conf(self):
        logger.info('Closing window ...\n')

        # Saving interface general values **********************************************************
        self.general_page_grid.save_selection()
        self.low_page_grid.save_selection()
        self.mid_page_grid.save_selection()
        self.high_page_grid.save_selection()

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

        mode = config.get('CONFIGURATION', 'modo_actual')

        self.animations(mode)

        reboot_indicators(mode)

        # Settings application
        command = 'pkexec slimbookbattery-pkexec apply'
        subprocess.Popen(command, shell=True, stdin=None, stdout=None, close_fds=True)

    def check_recommendations(self):
        def show_alert(data):
                dialog = PreferencesDialog(self, data)
                dialog.connect("destroy", self.close_dialog)
                dialog.show_all()   

        def check_tlp_version():
            data = {
                'title': _('Get last TLP version'),
                'info': _('We recommend you to add TLP repository, to get the last version of TLP ;)'),
                'btn_label': _('Add repository'),
                'command_lbl': _("Adding linrunner/TLP oficial repository.\nMake sure you have internet connection.\n"),
                'command': "sudo add-apt-repository ppa:linrunner/tlp && sudo apt-get update && sudo apt-get install tlp\n",
                'show_var': 'add-tlp-repository-alert'
            }

            cmd = 'cat /etc/apt/sources.list.d/* | grep "tlp"'
            code, str = subprocess.getstatusoutput(cmd)
            if not utils.get_version(TLP_VERSION) >= utils.get_version('1.5') and config.getboolean('CONFIGURATION', 'add-tlp-repository-alert') and code != 0 and VTE_VERSION[0] == 0:
                show_alert(data) 

        if check_tlp_version():
            pass

    def close_dialog(self, dialog):
        dialog.close()
        self.active = True


class TerminalWin(Gtk.Window):

    def __init__(self, parent, data):
        mytitle = data.get('title')
        command_lbl = Gtk.Label(label=data.get('command_lbl'))
        command = data.get('command')

        gi.require_version('Vte', '2.91')
        from gi.repository import GLib, Vte

        Gtk.Window.__init__(self, title=mytitle)
        self.set_default_size(600, 300)

        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.set_name('terminal')

        self.button_close = Gtk.Button(label="Close")
        self.button_close.set_halign(Gtk.Align.END)
        self.button_close.connect("clicked", self.close_win, parent)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.pack_start(command_lbl, False, True, 0)

        self.terminal = Vte.Terminal()
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,  # PtyFlags
            os.environ['HOME'],  # Dir
            ["/bin/bash"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,  # at least None is required
            None,
        )

        scroller = Gtk.ScrolledWindow()
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        scroller.add(self.terminal)
        box.pack_start(scroller, False, True, 2)
        box.pack_start(self.button_close, False, True, 0)
        self.add(box)

        self.terminal.show()
        self.InputToTerm(command)

    def feed(self, command, version, wait_until_done=True):
        command += '\n'
        if utils.get_version('0.60') > utils.get_version(version):
            length = len(command)
            self.terminal.feed_child(command, length)
        else:
            self.terminal.feed_child(command.encode("utf-8"))

    def InputToTerm(self, command):
        def first_letter(s):
            m = re.search(r'[a-z]', s, re.I)
            return m.start() if m is not None else -1

        # Check vte version
        if VTE_VERSION[0] == 0:
            try:
                version = VTE_VERSION[1][VTE_VERSION[1].find('Version:')+8:]
                version = version[:first_letter(version)]
                self.feed(command, version)
            except Exception:
                print('Failed to get current Vte version (except):', VTE_VERSION[0], VTE_VERSION[1])
        else:
            print('Failed to get current Vte version:', VTE_VERSION[0], VTE_VERSION[1])

    def close_win(self, button=None, parent=None):
        parent.close()
        self.close()
        self.destroy()


class PreferencesDialog(Gtk.Dialog):

    def __init__(self, parent, data):

        info = data.get('info')
        btn_label = data.get('btn_label')
        self.show_var = data.get('show_var')
        self.show_bool = True

        Gtk.Dialog.__init__(self,
                            title='',
                            parent=parent,
                            flags=0)

        # self.set_modal(True)
        self.set_transient_for(parent)

        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.get_style_context().add_class("bg-color")
        self.set_default_size(500, 0)
        self.set_decorated(False)
        self.set_name('warn')

        vbox = Gtk.VBox(homogeneous=False, spacing=5)
        vbox.set_border_width(5)

        self.get_content_area().add(vbox)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(info)
        self.textview.set_wrap_mode(Gtk.WrapMode(2))
        self.textview.set_pixels_inside_wrap(5)
        self.textview.set_pixels_above_lines(6)
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        vbox.pack_start(self.textview, True, True, 0)

        hbox = Gtk.HBox(spacing=5)
        hbox.set_border_width(5)
        hbox.set_margin_top(10)

        button_show = Gtk.CheckButton(label=_("Don't show again"))
        button_show.connect("clicked", self.not_show)
        hbox.pack_start(button_show, True, True, 0)

        button_install = Gtk.Button(label=btn_label)
        button_install.connect("clicked", self.on_button_ok, data)
        hbox.pack_start(button_install, True, True, 0)

        button_close = Gtk.Button(label=_("Cancel"))
        button_close.connect("button-press-event", self.on_button_close)
        hbox.pack_start(button_close, True, True, 0)

        vbox.pack_start(hbox, True, True, 0)

        self.active = True

    def on_button_ok(self, button, data):

        def show_terminal(data):
            win = TerminalWin(self, data)
            win.connect("delete-event", Gtk.main_quit)
            win.show_all()

        show_terminal(data)

    def not_show(self, button):
        self.show_bool = not button.get_active()

    def on_button_close(self, button, event=None):
        print('Setting', self.show_var, 'to', self.show_bool)

        if not self.show_bool:
            config.set('CONFIGURATION', self.show_var, str(self.show_bool))
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        self.destroy()


def reboot_indicators(mode=None):

    # Reboots battery indicator
    exit, msg = utils.reboot_process(
        'slimbookbatteryindicator.py',  # program to kill
        os.path.join(CURRENT_PATH, 'slimbookbatteryindicator.py'),  # Path to start indicator
    )
    if exit != 0:
        logger.error(msg)

    # If sync active, reboot tdp indicator
    if config.getboolean('TDP', 'saving_tdpsync'):
        logger.info(f'\n{Colors.GREEN}[TDP SETTINGS]{Colors.ENDC}')
        logger.info(f'Battery Mode: {mode}')

        # Mode settings & reboot
        if config.getboolean('CONFIGURATION', 'application_on'):
            tdp_utils.set_mode(mode)
            exit, msg = tdp_utils.reboot_indicator()
            if exit != 0:
                logger.error(msg)
        else:
            logger.info(f'App off, not changing {tdp_controller} mode configuration.')

    else:
        logger.info('TDP Sync not active')


if __name__ == "__main__":
    logger.setLevel(logging.ERROR)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.basicConfig(filename = "/home/slimbook/Escritorio/logfile.log",
                    filemode = "w",
                    format = formatter, 
                    level = logging.ERROR)

    win = Preferences()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
