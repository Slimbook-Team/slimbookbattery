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
import math
import os
import re
import shutil
import subprocess
import sys
import time
from distutils.dir_util import copy_tree

import gi

# We want load first current location
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
if CURRENT_PATH not in sys.path:
    sys.path = [CURRENT_PATH] + sys.path
import utils

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

logger = logging.getLogger()

USER_NAME = utils.get_user()
HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))

IMAGES_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '..', 'images'))
CONFIG_FOLDER = os.path.join(HOMEDIR, '.config/slimbookbattery')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'slimbookbattery.conf')

INTEL_ES = 'https://slimbook.es/es/tutoriales/aplicaciones-slimbook/515-slimbook-intel-controller'
INTEL_EN = 'https://slimbook.es/en/tutoriales/aplicaciones-slimbook/514-en-slimbook-intel-controller'
AMD_ES = 'https://slimbook.es/es/tutoriales/aplicaciones-slimbook/493-slimbook-amd-controller'
AMD_EN = 'https://slimbook.es/en/tutoriales/aplicaciones-slimbook/494-slimbook-amd-controller-en'

_ = utils.load_translation('preferences')

lang = utils.get_languages()[0]

config = configparser.ConfigParser()

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

        link = Gtk.LinkButton(uri="https://github.com/slimbook/slimbookbattery/tree/main/src/locale",
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
            _("Contact with us if you find something wrong. "),
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
            path = os.path.join(
                save_dialog.get_filename(),
                'report_{}.txt'.format(time.strftime("%d-%m-%y_%H:%M"))
            )
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
            'mapping': {
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
            },
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
                logger.error('Mapping not found for {}: {}'.format(content, data))
                continue
            header.set_markup('<b>{}</b>'.format(data.get('header', '')))
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

    def complete_values(self):
        content = None
        code, battery_raw = subprocess.getstatusoutput(
            "upower -i `upower -e | grep 'BAT'`"
        )
        battery_data = {}
        for line in battery_raw.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                battery_data[key.strip()] = value.strip()

        for data in self.FIELDS:
            label_name = data.get('label_name')
            if not (label_name and label_name in self.content):
                continue
            if 'mapping' in data:
                data = data.get('mapping', {}).get(content, {})
                if self.time_to_header:
                    self.time_to_header.set_markup('<b>{}</b>'.format(data.get('header', '')))

            content = _('Unknown')
            if 'filter' in data:
                if code == 0:
                    content = battery_data.get(data.get('filter'))
                    if data.get('filter') in ['time to empty', 'time to full']:
                        time_to = content.split()
                        if time_to[1] == 'hours':
                            content = '{}{}'.format(time_to[0], _(' hours'))
                        else:
                            content = '{}{}'.format(time_to[0], _(' min'))
            elif 'text' in data:
                content = data.get('text')

            label = self.content[label_name]
            label.set_label(content)


class GeneralGrid(BasePageGrid):
    tab_name = _('General')
    allow_minimize = False
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
        self.grid.set_halign(Gtk.Align.CENTER)
        if self.parent.min_resolution:
            self.grid.set_name('smaller_label')
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

        tdp_controller = config.get('TDP', 'tdpcontroller')
        code, msg = subprocess.getstatusoutput("cat /proc/cpuinfo | grep 'model name' | head -n1")
        if code != 0:
            logging.error(msg)
        else:
            if 'intel' in msg.lower():
                if tdp_controller != 'slimbookintelcontroller':
                    logging.info('Intel detected')
                tdp_controller = 'slimbookintelcontroller'
            elif 'amd' in msg.lower():
                if tdp_controller != 'slimbookamdcontroller':
                    logging.info('AMD detected')
                tdp_controller = 'slimbookamdcontroller'
            else:
                logging.error('Could not find TDP controller for your processor')

        if tdp_controller:
            row += 1
            config.set('TDP', 'tdpcontroller', tdp_controller)

            label = Gtk.Label(label=_('Synchronice battery mode with CPU TDP mode:'))
            label.set_halign(Gtk.Align.START)
            self.grid.attach(label, self.HEADER, row, 2, 1)

            button = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
            button.set_name('saving_tdpsync')
            button.connect('notify::active', self.manage_events)
            self.content['saving_tdpsync'] = button
            self.grid.attach(button, self.CONTENT, row, 1, 1)

            code, msg = subprocess.getstatusoutput('which ' + tdp_controller)
            if code != 0:
                logger.error('TDP Controller not installed')
                button.set_sensitive(False)
                button.set_state(False)

                if tdp_controller == 'slimbookintelcontroller':
                    if lang == 'es':
                        link = INTEL_ES
                    else:
                        link = INTEL_EN
                else:
                    if lang == 'es':
                        link = AMD_ES
                    else:
                        link = AMD_EN

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
            self.content['modo_actual_{}'.format(data.get('value'))] = toggle

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

        with open('/etc/tlp.conf') as f:
            content = f.read()
        if 'TLP_DEFAULT_MODE=AC' in content:
            self.content['working_failure'].set_active(0)
            self.work_mode = self.AC_MODE
        elif 'TLP_DEFAULT_MODE=BAT' in content:
            self.content['working_failure'].set_active(1)
            self.work_mode = self.BAT_MODE
        else:
            logger.error('WorkMode: Not found')

        current_mode = config.get('CONFIGURATION', 'modo_actual')
        button = self.content['modo_actual_{}'.format(current_mode)]
        button.set_active(True)

    def manage_events(self, button, *args):
        name = button.get_name()
        if name in ['saving_tdpsync']:
            config.set('TDP', name, '1' if button.get_active() else '0')
        elif name in ['application_on', 'icono', 'plug_warn']:
            config.set('CONFIGURATION', name, '1' if button.get_active() else '0')
        elif name == 'autostart':
            self.autostart_initial = button.get_active()
        else:
            if args:
                config.set('CONFIGURATION', 'modo_actual', args[0])

    def save_selection(self):
        button = self.content.get('working_failure')
        active = button.get_active_iter()
        if active is not None:
            model = button.get_model()
            work_mode = model[active][1]
            if work_mode and work_mode != self.work_mode:
                logger.info('Setting workmode {} ...'.format(work_mode))
                self.work_mode = work_mode
                code, msg = subprocess.getstatusoutput(
                    'pkexec slimbookbattery-pkexec change_config TLP_DEFAULT_MODE {}'.format(work_mode)
                )
                if code != 0:
                    logger.error(msg)

        if self.autostart_initial:
            destination = os.path.join(
                HOMEDIR, '.config/autostart'
            )
            if not os.path.isdir(destination):
                os.mkdir(destination)
            source = os.path.join(
                CURRENT_PATH, 'slimbookbattery-autostart.desktop'
            )
            if not os.path.isfile(os.path.join(destination, 'slimbookbattery-autostart.desktop')):
                logger.info('Enabling autostart ...')
                shutil.copy(source, destination)
                config.set('CONFIGURATION', 'autostart', '1')
        else:
            logger.info('Disabling autostart ...')
            autostart_path = os.path.join(HOMEDIR, '.config/autostart/slimbookbattery-autostart.desktop')
            if os.path.isfile(autostart_path):
                os.remove(autostart_path)
            config.set('CONFIGURATION', 'autostart', '0')

        reboot_process(
            'slimbookbatteryindicator.py',
            os.path.join(CURRENT_PATH, 'slimbookbatteryindicator.py'),
            config.getboolean('CONFIGURATION', 'icono')
        )

        tdp_controller = config.get('TDP', 'tdpcontroller')
        if config.getboolean('TDP', 'saving_tdpsync'):
            indicator = '{}indicator.py'.format(tdp_controller)
            indicator_full_path = os.path.join('/usr/share/', tdp_controller, 'src', indicator)
            reboot_process(indicator, indicator_full_path, True)
        else:
            logger.info('Mode not setting TDP')


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
            'help': _('Note: power save can cause an unstable wifi connection.'),
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
            'CPU_HWP_ON_AC': 'balance_performance',
            'CPU_HWP_ON_BAT': 'power',
            'ENERGY_PERF_POLICY_ON_AC': 'balance-performance',
            'ENERGY_PERF_POLICY_ON_BAT': 'power',
            'SCHED_POWERSAVE_ON_AC': 0,
            'SCHED_POWERSAVE_ON_BAT': 1,
        },
        2: {
            'CPU_MIN_PERF_ON_AC': 0,
            'CPU_MAX_PERF_ON_AC': 100,
            'CPU_MIN_PERF_ON_BAT': 0,
            'CPU_MAX_PERF_ON_BAT': 80,
            'CPU_BOOST_ON_AC': 1,
            'CPU_BOOST_ON_BAT': 0,
            'CPU_HWP_ON_AC': 'balance_performance',
            'CPU_HWP_ON_BAT': 'power',
            'ENERGY_PERF_POLICY_ON_AC': 'balance-performance',
            'ENERGY_PERF_POLICY_ON_BAT': 'power',
            'SCHED_POWERSAVE_ON_AC': 0,
            'SCHED_POWERSAVE_ON_BAT': 1,
        },
        3: {
            'CPU_MIN_PERF_ON_AC': 0,
            'CPU_MAX_PERF_ON_AC': 100,
            'CPU_MIN_PERF_ON_BAT': 0,
            'CPU_MAX_PERF_ON_BAT': 100,
            'CPU_BOOST_ON_AC': 1,
            'CPU_BOOST_ON_BAT': 1,
            'CPU_HWP_ON_AC': 'performance',
            'CPU_HWP_ON_BAT': 'power',
            'ENERGY_PERF_POLICY_ON_AC': 'balance-performance',
            'ENERGY_PERF_POLICY_ON_BAT': 'balance-performance',
            'SCHED_POWERSAVE_ON_AC': 0,
            'SCHED_POWERSAVE_ON_BAT': 1,
        },
    }

    @staticmethod
    def get_governor():
        governors = subprocess.getoutput(
            'for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_driver; do cat $i; done'
        ).split('\n')
        governor_driver = None
        for governor_driver in governors:
            if governor_driver not in ['intel_pstate', 'acpi-cpufreq', 'intel_cpufreq']:
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
        if self.parent.min_resolution:
            row = row + 1
        else:
            row = 1
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
                self.grid.attach(table_icon, label_col, row - row_correction, 3, 1)
            else:
                self.grid.attach(label, label_col, row - row_correction, 3, 1)

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
                button.connect('change-value', self.manage_events)

                button_on_off = Gtk.Switch(halign=Gtk.Align.END, valign=Gtk.Align.END)
                name = '{}_switch'.format(data.get('name'))
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

        with open(self.custom_file_path) as f:
            content = f.read()

        for key, search in {
            'sound': 'SOUND_POWER_SAVE_ON_BAT=1',
            'wifi_profile': 'WIFI_PWR_ON_BAT=on',
            'bluetooth_blacklist': 'USB_BLACKLIST_BTUSB=1',
            'printer_blacklist': 'USB_BLACKLIST_PRINTER=1',
            'ethernet_blacklist': 'USB_BLACKLIST_WWAN=1',
            'usb_shutdown': 'USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN=1',
        }.items():
            button = self.content[key]
            button.set_active(search in content)

        for key, search in {
            'disabled': 'DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE',
            'os': 'DEVICES_TO_DISABLE_ON_STARTUP',
        }.items():
            line = content[content.find(search):]
            line = line[:line.find('\n')]
            button_bluetooth = self.content['bluetooth_{}'.format(key)]
            button_bluetooth.set_active('bluetooth' in line)
            button_wifi = self.content['wifi_{}'.format(key)]
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
            else:
                # Setting default mode to save energy
                if self.custom_file == 'ahorrodeenergia':
                    active_mode = values.index('powersave')
                else:
                    active_mode = values.index('performance')
        elif governor in ['acpi-cpufreq', 'intel_cpufreq']:
            values = list(dict(self.CPUFREQ_GOV).values())
            if gov_mode in values:
                active_mode = values.index(gov_mode)
            else:
                # Setting default mode
                if self.custom_file == 'ahorrodeenergia':
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
        usb_autosuspend = bool('USB_AUTOSUSPEND=1' in content)
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
        with open(self.custom_file_path) as f:
            content = f.read()

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
                logger.info('[{}] Setting {} saving to "{}" --> Exit({}): {}'.format(
                    self.custom_file, search, value, code, msg
                ))

        value = config.getint('SETTINGS', self.SECTION_MAPPING[self.custom_file]['limit_cpu'])
        for search, value in self.CPU_LIMIT[value].items():
            if '{search}={value}'.format(search=search, value=value) not in content:
                cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
                code, msg = subprocess.getstatusoutput(cmd)
                logger.info('[{}] Setting {} saving to "{}" --> Exit({}): {}'.format(
                    self.custom_file, search, value, code, msg
                ))

        for key, search_items in {
            'sound': 'SOUND_POWER_SAVE_ON_BAT',
            'bluetooth_blacklist': 'USB_BLACKLIST_BTUSB USB_EXCLUDE_BTUSB',
            'printer_blacklist': 'USB_BLACKLIST_PRINTER USB_EXCLUDE_PRINTER',
            'ethernet_blacklist': 'USB_BLACKLIST_WWAN USB_EXCLUDE_WWAN',
            'usb_shutdown': 'USB_AUTOSUSPEND_DISABLE_ON_SHUTDOWN',
            'wifi_profile': 'WIFI_PWR_ON_BAT',
            'usb': 'USB_AUTOSUSPEND',
        }.items():

            button = self.content[key]
            if search_items == 'WIFI_PWR_ON_BAT':
                value = 'on' if button.get_active() else 'off'
            else:
                value = '1' if button.get_active() else '0'

            for search in search_items.split(' '):
                # print('{}'.format(Colors.RED)+search+'{}'.format(Colors.ENDC))
                if '{search}={value}'.format(search=search, value=value) not in content:
                    # print('{}Not in content{}'.format(Colors.GREEN, Colors.ENDC))
                    if search in content:
                        cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
                        code, msg = subprocess.getstatusoutput(cmd)
                        logger.info('[{}] Setting {} saving to "{}" --> Exit({}): {}'.format(
                            self.custom_file, search, value, code, msg
                        ))

        for key, search in {
            'disabled': 'DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE',
            'os': 'DEVICES_TO_DISABLE_ON_STARTUP',
        }.items():
            value = []
            button_bluetooth = self.content['bluetooth_{}'.format(key)]
            if button_bluetooth.get_active():
                value.append('bluetooth')
            button_wifi = self.content['wifi_{}'.format(key)]
            if button_wifi.get_active():
                value.append('wifi')
            value = ' '.join(value)
            cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
            code, msg = subprocess.getstatusoutput(cmd)
            logger.info('[{}] Setting {} saving to "{}" --> Exit({}): {}'.format(
                self.custom_file, search, value, code, msg
            ))

        button = self.content['wifi_lan']
        value = 'wifi' if button.get_active() else ''
        for search in ['DEVICES_TO_DISABLE_ON_LAN_CONNECT', 'DEVICES_TO_ENABLE_ON_LAN_DISCONNECT']:
            cmd = base_cmd.format(search=search, value=value, file=self.custom_file_path)
            code, msg = subprocess.getstatusoutput(cmd)
            logger.info('[{}] Setting {} saving to "{}" --> Exit({}): {}'.format(
                self.custom_file, search, value, code, msg
            ))

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
                    logger.info('[{}] Setting {} saving to "{}" --> Exit({}): {}'.format(
                        self.custom_file, search, value, code, msg
                    ))


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
        self.__setup_css()
        Gtk.Window.__init__(self, title=(_('Slimbook Battery Preferences')))

        self.get_style_context().add_class("bg-image")
        self.set_position(Gtk.WindowPosition.CENTER)  # // Allow movement

        self.set_size_request(0, 0)

        self.set_decorated(False)
        self.set_resizable(True)

        # Movement
        self.is_in_drag = False
        self.x_in_drag = 0
        self.y_in_drag = 0
        self.connect('button-press-event', self.on_mouse_button_pressed)
        self.connect('button-release-event', self.on_mouse_button_released)
        self.connect('motion-notify-event', self.on_mouse_moved)

        # Center
        # self.connect('realize', self.on_realize)
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
            self.child_process.terminate()

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

    def set_ui(self):
        self.set_default_icon(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'normal.png'),
            width=825,
            height=225,
            preserve_aspect_ratio=True)
        )

        display_width, display_height = utils.get_display_resolution()
        if display_width >= 1550 and display_height >= 850:
            logger.debug(_('Full window is displayed'))
        else:
            self.resize(1100, 650)
            self.min_resolution = True

        win_grid = Gtk.Grid(column_homogeneous=True,
                            column_spacing=0,
                            row_spacing=20)

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

        buttons_box = Gtk.Box()
        buttons_box.pack_start(btn_cancel, True, True, 0)
        buttons_box.pack_start(restore_values, True, True, 0)
        buttons_box.pack_start(btn_accept, True, True, 0)
        buttons_box.set_halign(Gtk.Align.END)

        if self.min_resolution:
            buttons_box.set_name('smaller_label')

        label_version = Gtk.Label(label='', halign=Gtk.Align.START)
        label_version.set_name('version')

        desk_config = configparser.ConfigParser()
        desk_config.read('/usr/share/applications/slimbookbattery.desktop')
        if desk_config.has_option('Desktop Entry', 'Version'):
            version = desk_config.get('Desktop Entry', 'Version')
        else:
            version = 'Unknown'
        label_version.set_markup('<span font="10">Version: {}</span>'.format(version))

        win_grid.attach(buttons_box, 0, 4, 1, 1)
        win_grid.attach(label_version, 0, 4, 1, 1)

        if not os.path.isfile(os.path.join(CONFIG_FOLDER, 'default/equilibrado')):
            logger.debug('Copy configuration files ...')
            base_folder = '/usr/share/slimbookbattery/'
            if not os.path.isdir(base_folder):
                base_folder = os.path.normpath(os.path.join(CURRENT_PATH, '..'))
            copy_tree(os.path.join(base_folder, 'default'), os.path.join(CONFIG_FOLDER, 'default'))
            copy_tree(os.path.join(base_folder, 'custom'), os.path.join(CONFIG_FOLDER, 'custom'))

        if self.min_resolution:
            height = 175
            width = 775
        else:
            height = 225
            width = 825

        logo = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(IMAGES_PATH, 'slimbookbattery-header-2.png'),
            width=width,
            height=height,
            preserve_aspect_ratio=True
        ))
        logo.set_halign(Gtk.Align.START)
        logo.set_valign(Gtk.Align.START)
        win_grid.attach(logo, 0, 0, 1, 4)

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

        check = Gtk.CheckButton.new_with_label(label=_('System style'))
        check.set_name('style')
        check.set_tooltip_text(_('Style will be changed once you reopen the preferences window.'))
        style = config.get('CONFIGURATION', 'style') if config.has_option('CONFIGURATION', 'style') else 'system'
        if style == 'system':
            check.set_active(True)

        check.connect('clicked', self.manage_events)

        close_box.add(check)
        close_box.add(event_close_box)
        win_grid.attach(close_box, 0, 0, 1, 4)

        # NOTEBOOK ***************************************************************

        notebook = Gtk.Notebook.new()
        if self.min_resolution:
            notebook.set_name('smaller_label')
            notebook.set_vexpand(True)
            notebook.set_hexpand(False)

        notebook.set_tab_pos(Gtk.PositionType.TOP)
        win_grid.attach(notebook, 0, 3, 1, 1)

        logger.debug("{}{} {}{}".format(
            _('Width: '), display_width,
            _(' Height: '), display_height
        ))

        # CREATE TABS
        self.general_page_grid = GeneralGrid(self)
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
        logger.info('\n')

    def manage_events(self, button, *args):
        name = button.get_name()
        if name == 'style':
            value = 'system' if button.get_active() else 'original'
            config.set('CONFIGURATION', 'style', value)
            # To do: restore css provider
            # self.hide()
            # self.__setup_css()
            # self.show_all()
        elif name == 'restore':
            os.system('pkexec slimbookbattery-pkexec restore')
            config.read(CONFIG_FILE)
            self.hide()

            win = Preferences()
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
        elif name == 'accept':
            self.apply_conf()

        if name in ['accept', 'close_box', 'cancel']:
            Gtk.main_quit()
            exit(0)

    def __setup_css(self):
        """Setup the CSS and load it."""
        style = 'original'
        if config.has_option('CONFIGURATION', 'style'):
            style = config.get('CONFIGURATION', 'style')

        provider_file = '{}/css/{}-style.css'.format(CURRENT_PATH, style)
        provider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        provider.load_from_path(provider_file)
        context.add_provider_for_screen(screen, provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        logger.debug("Loading CSS")

    def animations(self, mode):
        check_desktop = 'gnome' in os.environ.get("XDG_CURRENT_DESKTOP", '').lower()

        if check_desktop:
            logger.info('Setting mode ' + mode + ' animations')
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
            logger.info('Not Gnome desktop {} {}'.format(str(check_desktop[0]), check_desktop[1]))

    def apply_conf(self):
        logger.info('Closing window ...\n')

        # Saving interface general values **********************************************************

        self.general_page_grid.save_selection()
        self.low_page_grid.save_selection()
        self.mid_page_grid.save_selection()
        self.high_page_grid.save_selection()

        with open(os.path.join(CONFIG_FOLDER, 'slimbookbattery.conf'), 'w') as configfile:
            config.write(configfile)

        self.animations(config.get('CONFIGURATION', 'modo_actual'))

        # Settings application
        # command = 'pkexec slimbookbattery-pkexec apply'
        # print(subprocess.getoutput(command.split(' ')))
        os.system('pkexec slimbookbattery-pkexec apply')


def reboot_process(process_name, path, start):
    logger.info('Rebooting ' + process_name + ' ...')
    # logger.info(path)
    process = subprocess.getoutput('pgrep -f ' + process_name)
    # logger.info(process)

    # If it find a process, kills it
    if len(process.split('\n')) > 1:
        proc_list = process.split('\n')

        for i in range(len(proc_list) - 1):
            exit = subprocess.getstatusoutput('kill -9 ' + proc_list[i])
            logger.info('Killing process ' + proc_list[i] + ' Exit: ' + str(exit[0]))
            if exit[0] == 1:
                logger.info(exit[1])

        logger.info('Launching process...')
        if os.path.isfile(path):
            os.system('python3 {} &'.format(path))
            logger.info('Done')
        else:
            logger.info("Couldn't launch process")

    else:
        logger.info(process_name + ' was not running')

        if start:
            logger.info('Launching process...')
            if os.path.isfile(path):
                os.system('python3 {} &'.format(path))
                logger.info('Done\n')
            else:
                logger.info("Couldn't launch process\n")
    logger.info('\n')


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    win = Preferences()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
