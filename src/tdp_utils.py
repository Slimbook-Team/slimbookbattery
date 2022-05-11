import os, subprocess, utils
from configparser import ConfigParser

USER_NAME = utils.get_user(from_file='/tmp/slimbookbattery.user')
HOMEDIR = os.path.expanduser('~{}'.format(USER_NAME))
BATT_CONFIG_FOLDER = os.path.join(HOMEDIR, '.config/slimbookbattery')
BATT_CONFIG_FILE = os.path.join(BATT_CONFIG_FOLDER, 'slimbookbattery.conf')
battery_conf = ConfigParser()
battery_conf.read(BATT_CONFIG_FILE)

def get_tdp_controller():
    if battery_conf.has_option('TDP', 'tdpcontroller') and battery_conf.get('TDP', 'tdpcontroller')!='':
        tdp_controller = battery_conf.get('TDP', 'tdpcontroller')
    else:
        tdp_controller = ''
        code, msg = subprocess.getstatusoutput("cat /proc/cpuinfo | grep 'model name' | head -n1")
        if code == 0:
            if 'intel' in msg.lower():
                # print('Intel detected')
                tdp_controller = 'slimbookintelcontroller'
            elif 'amd' in msg.lower():
                # print('AMD detected')
                tdp_controller = 'slimbookamdcontroller'
            else:
                print('Could not find TDP controller for your processor')
            
    return tdp_controller

tdp_controller = get_tdp_controller()

TDP_CONFIG_FOLDER = os.path.join(HOMEDIR, '.config/{}'.format(tdp_controller))
TDP_CONFIG_FILE = os.path.join(TDP_CONFIG_FOLDER, '{}.conf'.format(tdp_controller))
tdp_conf = ConfigParser()
tdp_conf.read(TDP_CONFIG_FILE)

# Gets battery mode and parses it to tdp controller mode to sync it
def set_mode(mode):
    MAPPING_MODES = {
        '1': 'low',
        '2': 'medium',
        '3': 'high'
    }

    if mode in MAPPING_MODES:
        tdp_mode = MAPPING_MODES[mode]
    try:
        print('Updating TDP mode ...')
        tdp_conf.set('CONFIGURATION', 'mode', tdp_mode)
        print('  TDP changed to {}'.format(tdp_conf.get('CONFIGURATION', 'mode')))

        # Autostart settings
        print('\nUpdating TDP autostart ...')
        if battery_conf.getboolean('CONFIGURATION', 'autostart'):
            tdp_conf.set('CONFIGURATION', 'autostart', 'on')
            print('TDP Autostart enabled')

        configfile = open(TDP_CONFIG_FILE, 'w')
        tdp_conf.write(configfile)
        configfile.close()

        print('Actual TDP Mode: {}'.format(tdp_conf.get('CONFIGURATION', 'mode')))
    except Exception as e:
        print('Could not sync TDP', e)

def reboot_indicator():
    indicator = '{}indicator.py'.format(tdp_controller)
    indicator_full_path = os.path.join('/usr/share/', tdp_controller, 'src', indicator)
    exit, msg = utils.reboot_process(
                indicator, 
                indicator_full_path, 
            )
    return (exit, msg)
        
