#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import time


def gen_report(filepath, xdg_current_desktop, user_home):
    with open(filepath, 'w+') as f:
        f.write('#SLIMBOOK BATTERY REPORT ' + time.strftime("DATE: %d/%m/%y TIME: %H:%M:%S") + '#\n')
        f.write('#######################################################\n\n')
        f.write('#BRAND AND MODEL\n')
        f.write('Brand: ' + subprocess.getoutput("dmidecode -s system-product-name") + '\n')
        f.write('Model: ' + subprocess.getoutput("dmidecode -s baseboard-manufacturer") + '\n\n')
        f.write('#BIOS INFORMATION\n')
        f.write(subprocess.getoutput("dmidecode -t bios") + '\n\n')
        f.write('#PCI BUSES AND DEVICES CONNECTED TO THESE\n')
        f.write(subprocess.getoutput("lspci") + '\n\n')
        f.write('#CPU STADISTICS\n')
        f.write(subprocess.getoutput("tlp-stat -p") + '\n')
        f.write(subprocess.getoutput("dmidecode -t processor") + '\n\n')
        f.write('#GPU STADISTICS\n')
        f.write(subprocess.getoutput("tlp-stat -g") + '\n\n')
        f.write('#MEMORY RAM STADISTICS\n')
        f.write(subprocess.getoutput("free --human") + '\n')
        f.write(subprocess.getoutput("dmidecode -t memory") + '\n\n')
        f.write('#DISK DEVICES STADISTICS\n')
        f.write(subprocess.getoutput("tlp-stat -d") + '\n\n')
        f.write('#USB DEVICES CONNECTED\n')
        f.write(subprocess.getoutput("lsusb") + '\n\n')
        f.write('#DIRECTORIES INSIDE /sys/class/power_supply/\n')
        f.write(subprocess.getoutput("ls /sys/class/power_supply/") + '\n')
        f.write('#BAT/ADP FILES\n')
        f.write(subprocess.getoutput("ls /sys/class/power_supply/*/") + '\n\n')
        f.write('#BATTERY STADISTICS\n')
        f.write(subprocess.getoutput("upower -i `upower -e | grep 'BAT'`") + '\n')
        f.write('#DIRECTORIES INSIDE /sys/class/backlight/\n')
        f.write(subprocess.getoutput("ls /sys/class/backlight/") + '\n\n')
        f.write(subprocess.getoutput("cat /sys/class/backlight/*") + '\n\n')
        f.write('#BRIGHTNESS FILES\n')
        f.write(subprocess.getoutput("ls /sys/class/backlight/*/") + '\n\n')
        f.write('#CURRENT DESKTOP IN USE\n')
        f.write(xdg_current_desktop + '\n\n')
        f.write('#SYSTEM WARNINGS/ERROR/CRITIC MESSAGES\n')
        f.write(subprocess.getoutput("dmesg --level=warn") + '\n\n')
        f.write(subprocess.getoutput("dmesg --level=err") + '\n\n')
        f.write(subprocess.getoutput("dmesg --level=crit") + '\n\n')
        f.write('#SERVICE TLP STATUS\n')
        f.write(subprocess.getoutput("systemctl status tlp.service") + '\n\n')
        f.write('#IMPORTANT TLP STADISTICS\n')
        f.write(subprocess.getoutput("tlp-stat -c -s") + '\n\n')
        f.write('#SLIMBOOK BATTERY CONFIGURATION FILE\n')
        f.write(subprocess.getoutput("cat {}/.config/slimbookbattery/slimbookbattery.conf".format(user_home)) + '\n\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SlimbookBattery report')
    'filepath, xdg_current_desktop, user_home'
    parser.add_argument('filepath', type=str, nargs=1, help='File path where save the report')
    parser.add_argument('xdg_desktop', type=str, nargs='?', help='XDG_CURRENT_DESKTOP environment')
    parser.add_argument('user_home', type=str, nargs='?', help='User home path')

    options = parser.parse_args()
    xdg_desktop = options.xdg_desktop
    if not xdg_desktop:
        xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP')
    user_path = options.user_home
    if not user_path:
        user_path = os.path.expanduser("~")
    else:
        if not os.path.isdir(user_path):
            user_path = os.path.expanduser("~{}".format(user_path))
        if not os.path.isdir(user_path):
            parser.exit(1, 'Home path not found')

    gen_report(options.filepath[0], xdg_desktop, user_path)
