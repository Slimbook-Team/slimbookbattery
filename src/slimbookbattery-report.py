#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import time


# Genera el archivo del report
def main(ruta, escritorio, user):
    reportText = '#SLIMBOOK BATTERY REPORT ' + time.strftime("DATE: %d/%m/%y TIME: %H:%M:%S") + '#\n'
    reportText = reportText + '#######################################################\n\n'
    reportText = reportText + '#BRAND AND MODEL\n'
    reportText = reportText + 'Brand: ' + subprocess.getoutput("dmidecode -s system-product-name") + '\n'
    reportText = reportText + 'Model: ' + subprocess.getoutput("dmidecode -s baseboard-manufacturer") + '\n\n'
    reportText = reportText + '#BIOS INFORMATION\n'
    reportText = reportText + subprocess.getoutput("dmidecode -t bios") + '\n\n'
    reportText = reportText + '#PCI BUSES AND DEVICES CONNECTED TO THESE\n'
    reportText = reportText + subprocess.getoutput("lspci") + '\n\n'
    reportText = reportText + '#CPU STADISTICS\n'
    reportText = reportText + subprocess.getoutput("tlp-stat -p") + '\n'
    reportText = reportText + subprocess.getoutput("dmidecode -t processor") + '\n\n'
    reportText = reportText + '#GPU STADISTICS\n'
    reportText = reportText + subprocess.getoutput("tlp-stat -g") + '\n\n'
    reportText = reportText + '#MEMORY RAM STADISTICS\n'
    reportText = reportText + subprocess.getoutput("free --human") + '\n'
    reportText = reportText + subprocess.getoutput("dmidecode -t memory") + '\n\n'
    reportText = reportText + '#DISK DEVICES STADISTICS\n'
    reportText = reportText + subprocess.getoutput("tlp-stat -d") + '\n\n'
    reportText = reportText + '#USB DEVICES CONNECTED\n'
    reportText = reportText + subprocess.getoutput("lsusb") + '\n\n'
    reportText = reportText + '#DIRECTORIES INSIDE /sys/class/power_supply/\n'
    reportText = reportText + subprocess.getoutput("ls /sys/class/power_supply/") + '\n'
    reportText = reportText + '#BAT/ADP FILES\n'
    reportText = reportText + subprocess.getoutput("ls /sys/class/power_supply/*/") + '\n\n'
    reportText = reportText + '#BATTERY STADISTICS\n'
    reportText = reportText + subprocess.getoutput("upower -i `upower -e | grep 'BAT'`") + '\n'
    reportText = reportText + '#DIRECTORIES INSIDE /sys/class/backlight/\n'
    reportText = reportText + subprocess.getoutput("ls /sys/class/backlight/") + '\n\n'
    reportText = reportText + subprocess.getoutput("cat /sys/class/backlight/*") + '\n\n'
    reportText = reportText + '#BRIGHTNESS FILES\n'
    reportText = reportText + subprocess.getoutput("ls /sys/class/backlight/*/") + '\n\n'
    reportText = reportText + '#CURRENT DESKTOP IN USE\n'
    reportText = reportText + escritorio + '\n\n'
    reportText = reportText + '#SYSTEM WARNINGS/ERROR/CRITIC MESSAGES\n'
    reportText = reportText + subprocess.getoutput("dmesg --level=warn") + '\n\n'
    reportText = reportText + subprocess.getoutput("dmesg --level=err") + '\n\n'
    reportText = reportText + subprocess.getoutput("dmesg --level=crit") + '\n\n'
    reportText = reportText + '#SERVICE TLP STATUS\n'
    reportText = reportText + subprocess.getoutput("systemctl status tlp.service") + '\n\n'
    reportText = reportText + '#IMPORTANT TLP STADISTICS\n'
    reportText = reportText + subprocess.getoutput("tlp-stat -c -s") + '\n\n'
    reportText = reportText + '#SLIMBOOK BATTERY CONFIGURATION FILE\n'
    reportText = reportText + subprocess.getoutput(
        "cat " + user + "/.config/slimbookbattery/slimbookbattery.conf") + '\n\n'

    f = open(ruta, 'w+')
    f.write(reportText)
    f.close()


if __name__ == "__main__":
    # Se obtiene las variables que se le pasa desde el archivo preferences
    main(sys.argv[1], sys.argv[2], sys.argv[3])
