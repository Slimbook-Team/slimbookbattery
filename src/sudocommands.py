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

#This file will be executed as sudo by pkexec
import os
import sys
import subprocess
import gi
from configparser import ConfigParser
import re
import gettext
import locale

#gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf

print('******************************************************************************')


print('\x1b[6;30;42m'+'SlimbookBattery-Commandline, executed as: '+str(subprocess.getoutput('whoami'))+'\x1b[0m')

if subprocess.getstatusoutput("logname")[0]==0:
    USER_NAME = subprocess.getoutput("logname")
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
currpath = os.path.dirname(os.path.realpath(__file__))

print("Username: "+USER_NAME+" - Homedir: "+HOMEDIR+"")


config_file = HOMEDIR+'/.config/slimbookbattery/slimbookbattery.conf'


config = ConfigParser()
config.read(config_file)

tdpcontroller = config['TDP']['tdpcontroller']
tdp_config_file = HOMEDIR+'/.config/'+tdpcontroller+'/'+tdpcontroller+'.conf'

config_tdp = ConfigParser()
config_tdp.read(tdp_config_file)


try:
    entorno_usu = locale.getlocale()[0]
    if entorno_usu.find("en") >= 0 or entorno_usu.find("es") >= 0 or entorno_usu.find("it") >= 0 or entorno_usu.find("pt") >= 0 or entorno_usu.find("gl") >= 0:
        idiomas = [entorno_usu]
    else:
        idiomas = ['en']
    print('Language: ', entorno_usu)
except:
    idiomas = ['en']

t = gettext.translation('slimbookbattery',
                        currpath+'/locale',
                        languages=idiomas,
                        fallback=True)

_ = t.gettext

def main(args): # Args will be like --> command_name value
    # notification = Notify.Notification.new('ssssss', 'aaaaaaaaaaaaa', None)
    # Notify.init('Slimbook Battery')
    # Notify.Notification.new('ssssss', 'aaaaaaaaaaaaa', None).show()

    arguments = ''

    for argument in range(len(args)):
        if argument != 0:
            arguments = arguments+' '+(args[argument])

    print("Arguments: "+ arguments+"\n")
    
    if (len(args)) > 1:
        battery_mode = config.get('CONFIGURATION', 'modo_actual')
        # Applies selected mode conf and turns on/off tlp  
        if args[1] == "apply": 
            
            # Copies selected custom mode conf to /etc/tlp.conf
            if battery_mode == '1':
                print('Power saving mode')
                subprocess.getstatusoutput("sudo cp "+HOMEDIR+"/.config/slimbookbattery/custom/ahorrodeenergia /etc/tlp.conf")
                
            elif battery_mode == '2':
                print('Normal power mode')
                os.system("sudo cp "+HOMEDIR+"/.config/slimbookbattery/custom/equilibrado /etc/tlp.conf")

            elif battery_mode == '3':
                print('Full power mode')
                os.system("sudo cp "+HOMEDIR+"/.config/slimbookbattery/custom/maximorendimiento /etc/tlp.conf")

            # Sets brightness
            print()
            brightness_settings(battery_mode)
            print()
            set_tdp(battery_mode)

            
            if config.get('CONFIGURATION', 'application_on') == '1':    # Sets mode changes and enables/disables TLP according to conf
                # Extra configuration
                required_reboot = mode_settings(battery_mode)
             
                print('\nApplication is on ...')

                # If it's not active in config, we activate it
                if subprocess.getstatusoutput("cat /etc/tlp.conf | grep 'TLP_ENABLE=0'")[0] == 0:
                    os.system("sed -i 's/TLP_ENABLE=0/ cTLP_ENABLE=1/' /etc/tlp.conf")                  
            
            else:   # Disablig TLP in conf
                
                if subprocess.getstatusoutput("cat /etc/tlp.conf | grep 'TLP_ENABLE=1'")[0] == 0:
                    os.system("sed -i 's/TLP_ENABLE=1/ cTLP_ENABLE=0/' /etc/tlp.conf")

                print('\tDisabled')

            # Restarting TLP
            os.system("sudo tlp start")

            if required_reboot == 1:
                print('Sudo notify')
                notify(_('Graphics settingshabe been modified,\nthe changes will be applied on restart.'))

            #print(str(os.system(command)))

            print('Required reboot --> Exit should be: '+str(required_reboot))
            exit(required_reboot)

        if args[1] == "restore": 

            # Copies selected DEFAULT conf to CUSTOM conf (also slimbookbattery.conf)
            print(str(subprocess.getstatusoutput("sudo cp /usr/share/slimbookbattery/src/slimbookbattery.conf "+ HOMEDIR+"/.config/slimbookbattery/slimbookbattery.conf")[0]))
            print(str(subprocess.getstatusoutput("sudo cp "+HOMEDIR+"/.config/slimbookbattery/default/ahorrodeenergia "+ HOMEDIR+"/.config/slimbookbattery/custom/ahorrodeenergia")[0]))
            print(str(subprocess.getstatusoutput("sudo cp "+HOMEDIR+"/.config/slimbookbattery/default/equilibrado "+ HOMEDIR+"/.config/slimbookbattery/custom/equilibrado")[0]))
            print(str(subprocess.getstatusoutput("sudo cp "+HOMEDIR+"/.config/slimbookbattery/default/maximorendimiento "+ HOMEDIR+"/.config/slimbookbattery/custom/maximorendimiento")[0]))

            #
            if battery_mode == '1':
                print('Power saving mode selected')
                subprocess.getstatusoutput("sudo cp "+HOMEDIR+"/.config/slimbookbattery/custom/ahorrodeenergia /etc/tlp.conf")

            elif battery_mode == '2':
                print('Normal power mode selected')
                os.system("sudo cp "+HOMEDIR+"/.config/slimbookbattery/custom/equilibrado /etc/tlp.conf")

            elif battery_mode == '3':
                print('Full power mode selected')
                os.system("sudo cp "+HOMEDIR+"/.config/slimbookbattery/custom/maximorendimiento /etc/tlp.conf")
           
        
        if args[1] == "autostart":  # Sets brigthnes and enables tdp
            battery_mode = config.get('CONFIGURATION', 'modo_actual')
            brightness_settings(battery_mode)
        
        if args[1] == "report": 
            os.system("sudo python3 "+currpath+"/slimbookbattery-report.py "+ args[2] +' '+ args[3] +' '+ args[4])

        if args[1] == "restart_tlp":
            print('Restarting TLP...')
            os.system("sudo tlp start")
        
        if args[1] == "service":  # Manages slimbookbattery.service
            if args[2]=="start":
                os.system('sudo systemctl start slimbookbattery.service')

            elif args[2]=="stop":
                os.system('sudo systemctl stop slimbookbattery.service')

            elif args[2]=="create":   
                os.system('sudo cp /usr/share/slimbookbattery/src/service/slimbookbattery.service /lib/systemd/system/slimbookbattery.service')
                os.system('sudo chmod 755 /usr/share/slimbookbattery/src/service/slimbookbatteryservice.sh')
        
        if args[1] == "change_config": 
            change_config(args)

    print('******************************************************************************\n')  

def notify(msg):
    os.system('''display=":$(ls /tmp/.X11-unix/* | sed 's#/tmp/.X11-unix/X##' | head -n 1)"
                            user=$(who | grep '('$display')' | awk '{print $1}' | head -n 1)
                            uid=$(id -u $user)
                            sudo -u $user DISPLAY=$display DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$uid/bus notify-send "Slimbook Battery" "'''+msg+'''"
                            ''')
def set_tdp(mode):
    # This function enables tdpcontroller autostart an changes it's mode if battery application, 
    # battery autostart and sync tdp switch of the selected mode is on.
    
    print('[TDP SETTINGS]')
    print('Battery Mode: '+mode)

    # Mode settings
    if config['CONFIGURATION']['application_on'] == '1' :
        
        tdp_switch = ''
        tdp_mode = ''

        if mode == '1':
            tdp_switch = 'saving_tdpsync'
            tdp_mode = 'low'

        elif mode == '2':
            tdp_switch = 'balanced_tdpsync'
            tdp_mode = 'medium'

        elif mode == '3':
            tdp_switch = 'power_tdpsync'
            tdp_mode = 'high'

        #print('TDP switch '+tdp_switch, config['TDP'][tdp_switch], mode)

        try:
            if config['TDP'][tdp_switch] == '1':
                print('Updating TDP mode ...')
                config_tdp.set('CONFIGURATION','mode', tdp_mode)
                print('  TDP changed to '+config_tdp['CONFIGURATION']['mode']) 

                # Autostart settings
                print('\nUpdating TDP autostart ...')
                if config['CONFIGURATION']['autostart'] == '1':
                    config_tdp.set('CONFIGURATION','autostart','on')
                    print('  TDP Autostart enabled')
                    if config_tdp['CONFIGURATION']['show-icon'] == 'on':
                        print('  TDP Icon will be shown')
                    else:
                        config_tdp.set('CONFIGURATION','show-icon','off')
            else: 
                print('TDP Sync not active')

        except:
            print('Could not sync TDP')

    else: 
        print('Not changing '+tdpcontroller+' mode configuration.')

    configfile = open(tdp_config_file, 'w')
    config_tdp.write(configfile)
    configfile.close()

    print('Actual TDP Mode: '+config_tdp['CONFIGURATION']['mode'])    

def change_config(args): # For general page options
    
    file = '/etc/tlp.conf'
    file_ahorro = '/usr/share/slimbookbattery/custom/ahorrodeenergia'
    file_equilibrado = '/usr/share/slimbookbattery/custom/equilibrado'
    file_max = '/usr/share/slimbookbattery/custom/maximorendimiento'

    # TLP_DEFAULT_MODE      
    if args[2] == "TLP_DEFAULT_MODE":
        #Lo editamos en tlp.conf?
        if args[3]=='BAT':
            print('Selecting BAT')
            update_config(file, 'TLP_DEFAULT_MODE', 'BAT')
            update_config(file_ahorro, 'TLP_DEFAULT_MODE', 'BAT')
            update_config(file_equilibrado, 'TLP_DEFAULT_MODE', 'BAT')
            update_config(file_max, 'TLP_DEFAULT_MODE', 'BAT')
            
        elif args[3]=='AC':
            print('Selecting AC')
            update_config(file, 'TLP_DEFAULT_MODE', 'AC')
            update_config(file_ahorro, 'TLP_DEFAULT_MODE', 'AC')
            update_config(file_equilibrado, 'TLP_DEFAULT_MODE', 'AC')
            update_config(file_max, 'TLP_DEFAULT_MODE', 'AC')

        else:
            print("Err: Couldn't find 2nd parameter")

        print()
    
def mode_settings(mode):
    required_reboot = 0
    print('\n[MODE SETTINGS]')
    file_ahorro = HOMEDIR+'/.config/slimbookbattery/custom/ahorrodeenergia'
    file_equilibrado = HOMEDIR+'/.config/slimbookbattery/custom/equilibrado'
    file_max = HOMEDIR+'/.config/slimbookbattery/custom/maximorendimiento'

    graficaNvidia = False
    graphics_before = ''

    # Checking graphics
    stout = subprocess.getoutput('prime-select query')
    nvidia = subprocess.getstatusoutput("prime-select "+ stout +"| grep -i 'profile is already set'")
    if nvidia[0] == 0:  #
        graficaNvidia = True
        graphics_before = stout

    # If nvidia driver is installed and works WE SET IT MANUALLY
    if graficaNvidia == True:
        print('Detected nvidia graphics profile: '+graphics_before)
        print('Setting new profile ...')
        if mode =='1':
                  
            if config['SETTINGS']['graphics_ahorro'] == '1' and graphics_before != 'intel':
                if not graphics_before == 'intel':
                    os.system('prime-select intel')
            
            elif config['SETTINGS']['graphics_ahorro'] == '0' and graphics_before != 'on-demand':
                if not graphics_before == 'on-demand':
                    os.system('prime-select intel')
                    # avocado
                    os.system('prime-select on-demand')
            
        elif mode =='2':

            if config['SETTINGS']['graphics_equilibrado'] == '1' and graphics_before != 'on-demand':   
                if not graphics_before == 'on-demand':           
                    os.system('prime-select intel')
                    os.system('prime-select on-demand')
            
            elif config['SETTINGS']['graphics_equilibrado'] == '0' and graphics_before != 'nvidia':
                if not graphics_before == 'nvidia':
                    os.system('prime-select nvidia')
        
        elif mode =='3':
            if not graphics_before == 'nvidia':
                os.system('prime-select nvidia')


        graphics_after = subprocess.getoutput('prime-select query')
        print('Graphics before --> '+graphics_before+' // Graphics after --> '+ graphics_after)
        if not graphics_before == graphics_after:
            print('Required reboot changes to 1')
            required_reboot = 1
        
    # If nvidia driver is not installed or does not work, we use TLP
    elif graficaNvidia == False:   
        print('Setting graphics frequency ...')
        # GRAPHICS AMD SETTINGS de
        RADEON_POWER_PROFILE_ON_BAT='default'
        RADEON_DPM_STATE_ON_BAT='battery'
        RADEON_DPM_PERF_LEVEL_ON_BAT='auto'

        # GRAPHICS INTEL SETTINGS
        freq_table =''
        freq_available = ''

        if os.path.isfile('/sys/kernel/debug/dri/0/i915_ring_freq_table'):
            freq_table = subprocess.getoutput('cat /sys/kernel/debug/dri/0/i915_ring_freq_table')
            freq_table = freq_table.split('\n')
            freq_table.pop(0)
            freq_available = ''

            for i in freq_table:
                valor = i.split()
                freq_available = freq_available + ' ' + valor[0]

            freq_available = freq_available.strip().split(' ')       
        
            # FRECUENCIAS PARA LOS MODOS  
            if len(freq_available)>1:

                freqCorrecta = True
                min_bat = 0
                min_ac = 0
                max_bat = 0
                max_ac = 0
                boost_bat = 0
                boost_ac = 0

        if mode == '1':

            #if config['SETTINGS']['graphics_ahorro'] == '1' and os.system('lscpu | grep model | grep Radeon'):
            if config['SETTINGS']['graphics_ahorro'] == '1':           
                # Radeon integrated
                if subprocess.getstatusoutput('lscpu | grep -i model | grep  -i Radeon')[0]==0 :
                    print('Radeon graphics power profile: low')
                    RADEON_POWER_PROFILE_ON_BAT='low'
                    os.system('sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ c'+RADEON_POWER_PROFILE_ON_BAT+'" '+ file_ahorro)
                    os.system('sed -i "/RADEON_DPM_STATE_ON_BAT=/ c'+RADEON_POWER_PROFILE_ON_BAT+'" '+ file_ahorro)
                    os.system('sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ c'+RADEON_DPM_PERF_LEVEL_ON_BAT+'" '+ file_ahorro)
                
                # Intel integrated
                elif subprocess.getstatusoutput('lspci | grep VGA | grep -i Intel')[0] == 0 : 
                    print('Intel graphics power profile: low')       
                    # MIN_BAT/MIN_AC
                    #Si el valor que queremos se encuentra dentro del array se usará ese, sino se buscara dentro del array dentro del rango que se indica
                    for i in range(len(freq_available)):
                        if(int(freq_available[i]) > 0 and int(freq_available[i]) < 600):
                            min_bat = int(freq_available[i])
                            min_ac = int(freq_available[i])
                            break   

                    #Si el valor que se busca no se encuentra, el boolean freqCorrecta pasará a False y por lo tanto no se realizará ninguna modificación respecto a gráficas Intel
                    if min_bat == 0 or min_ac == 0:
                        freqCorrecta = False

                    # MAX_BAT/MAX_AC
                    if freqCorrecta == True:
                        for i in range(len(freq_available)):
                            if(int(freq_available[i]) >= 600 and int(freq_available[i]) < 800):
                                max_bat = int(freq_available[i])
                                break
                        if max_bat == 0:
                            freqCorrecta = False

                        if int(freq_available[-1]) > 0 and freqCorrecta == True:
                            max_ac = int(freq_available[-1])
                        if max_ac == 0:
                            freqCorrecta = False
                        
                        # BOOST_BAT/BOOST_AC
                        if freqCorrecta == True:
                            for i in range(len(freq_available)):
                                if(int(freq_available[i]) >= 800 and int(freq_available[i]) < int(freq_available[-1])):
                                    boost_bat = int(freq_available[i])
                                    break
                            if boost_bat == 0:
                                freqCorrecta = False

                            if int(freq_available[-1]) > 0 and freqCorrecta == True:
                                boost_ac = int(freq_available[-1])
                            if boost_ac == 0:
                                freqCorrecta = False

                    #Si el boolean sigue en True querrá decir que se han obtenido valores para min, max y boost y se llamará al script para poder realizar las modificaciones
                    if freqCorrecta == True:
                        print('Setting GPU freq --> '+str(min_bat), str(max_bat), str(boost_bat))
                        update_config(file_ahorro,'INTEL_GPU_MIN_FREQ_ON_BAT', str(min_bat))
                        update_config(file_ahorro,'INTEL_GPU_MIN_FREQ_ON_AC', str(min_ac))
                        update_config(file_ahorro,'INTEL_GPU_MAX_FREQ_ON_BAT', str(max_bat))
                        update_config(file_ahorro,'INTEL_GPU_MAX_FREQ_ON_AC', str(max_ac))
                        update_config(file_ahorro,'INTEL_GPU_BOOST_FREQ_ON_BAT', str(boost_bat))
                        update_config(file_ahorro,'INTEL_GPU_BOOST_FREQ_ON_AC', str(boost_ac)) 
                    else:
                        print('Frequency not changed')
                else:
                    print('Graphics 404')
            else:
                # Radeon integrated
                if subprocess.getstatusoutput('lscpu | grep -i model | grep -i Radeon')[0]== 0:
                    print('Radeon graphics power profile: low')
                    RADEON_POWER_PROFILE_ON_BAT='default'
                    os.system('sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ c'+RADEON_POWER_PROFILE_ON_BAT+'" '+ file_ahorro)
                    os.system('sed -i "/RADEON_DPM_STATE_ON_BAT=/ c'+RADEON_POWER_PROFILE_ON_BAT+'" '+ file_ahorro)
                    os.system('sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ c'+RADEON_DPM_PERF_LEVEL_ON_BAT+'" '+ file_ahorro)
                
                # Intel integrated
                elif subprocess.getstatusoutput('lspci | grep VGA | grep Intel')[0]== 0:
                    print('Intel graphics power profile: low')
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_BAT=/ c#INTEL_GPU_MIN_FREQ_ON_BAT=0" '+ file_ahorro)
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_AC=/ c#INTEL_GPU_MIN_FREQ_ON_AC=0" '+ file_ahorro)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_BAT=/ c#INTEL_GPU_MAX_FREQ_ON_BAT=0" '+ file_ahorro)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_AC=/ c#INTEL_GPU_MAX_FREQ_ON_AC=0" '+ file_ahorro)
                    os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_BAT=/ c#INTEL_GPU_BOOST_FREQ_ON_BAT=0" '+ file_ahorro)
                    os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_AC=/ c#INTEL_GPU_BOOST_FREQ_ON_AC=0" '+ file_ahorro)
                else:
                    print('Graphics 404')           
 
        if mode == '2':

            if config['SETTINGS']['graphics_equilibrado'] == '1':
                # Radeon integrated
                if subprocess.getstatusoutput('lscpu | grep -i model | grep  -i Radeon')[0]==0 :
                    print('Radeon graphics power profile: mid')
                    RADEON_POWER_PROFILE_ON_BAT='mid'
                
                # Intel integrated
                elif subprocess.getstatusoutput('lspci | grep VGA | grep -i Intel')[0]==0 :
                    print('Intel graphics power profile: low')
                    for i in range(len(freq_available)):
                        if(int(freq_available[i]) > 0 and int(freq_available[i]) < 600):
                            min_bat = int(freq_available[i])
                            #print('min_bat = '+str(min_bat))
                            min_ac = int(freq_available[i])
                            break
                    #Si el valor que se busca no se encuentra, el boolean freqCorrecta pasará a False y por lo tanto no se realizará ninguna modificación respecto a gráficas Intel
                    if min_bat == 0:
                        freqCorrecta = False
                    if min_ac == 0:
                        freqCorrecta = False


                    if freqCorrecta == True:
                        for i in range(len(freq_available)):
                            if(int(freq_available[i]) >= 900 and int(freq_available[i]) < 1000):
                                max_bat = int(freq_available[i])
                                #print('max_bat = '+str(max_bat))
                                break
                    if max_bat == 0:
                        freqCorrecta = False

                    if int(freq_available[-1]) > 0 and freqCorrecta == True:
                        max_ac = int(freq_available[-1])
                    if max_ac == 0:
                        freqCorrecta = False

                    if '1000' in freq_available and freqCorrecta == True:
                        boost_bat = 1000

                    if freqCorrecta == True:
                        for i in range(len(freq_available)):
                            if(int(freq_available[i]) >= 1000 and int(freq_available[i]) < int(freq_available[-1])):
                                boost_bat = int(freq_available[i])
                                #print('boost_bat = '+str(boost_bat))
                                break
                        if boost_bat == 0:
                            freqCorrecta = False

                    if int(freq_available[-1]) > 0 and freqCorrecta == True:
                        boost_ac = int(freq_available[-1])
                    if boost_ac == 0:
                        freqCorrecta = False
                    
                    #Si el boolean sigue en True querrá decir que se han obtenido valores para min, max y boost y se llamará al script para poder realizar las modificaciones
                    if freqCorrecta == True:
                        print('Setting GPU freq --> '+str(min_bat), str(max_bat), str(boost_bat))
                        update_config(file_equilibrado,'INTEL_GPU_MIN_FREQ_ON_BAT', str(min_bat))
                        update_config(file_equilibrado,'INTEL_GPU_MIN_FREQ_ON_AC', str(min_ac))
                        update_config(file_equilibrado,'INTEL_GPU_MAX_FREQ_ON_BAT', str(max_bat))
                        update_config(file_equilibrado,'INTEL_GPU_MAX_FREQ_ON_AC', str(max_ac))
                        update_config(file_equilibrado,'INTEL_GPU_BOOST_FREQ_ON_BAT', str(boost_bat))
                        update_config(file_equilibrado,'INTEL_GPU_BOOST_FREQ_ON_AC', str(boost_ac))
                    else:
                        print('Freq not found')
            else:
                # Radeon integrated
                if subprocess.getstatusoutput('lscpu | grep -i model | grep -i Radeon')[0]== 0:
                    print('Radeon graphics power profile: mid')
                    RADEON_POWER_PROFILE_ON_BAT='default'
                    os.system('sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ c#RADEON_POWER_PROFILE_ON_BAT='+RADEON_POWER_PROFILE_ON_BAT+'" '+ file_equilibrado)
                    os.system('sed -i "/RADEON_DPM_STATE_ON_BAT=/ c#RADEON_DPM_STATE_ON_BAT=0'+RADEON_DPM_STATE_ON_BAT+'" '+ file_equilibrado)
                    os.system('sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ c#RADEON_DPM_PERF_LEVEL_ON_BAT='+RADEON_DPM_PERF_LEVEL_ON_BAT+'" '+ file_ahorro)
                          
                # Intel integrated
                elif subprocess.getstatusoutput('lspci | grep VGA | grep Intel')[0]== 0:
                    print('Intel graphics power profile: mid')
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_BAT=/ c#INTEL_GPU_MIN_FREQ_ON_BAT=0" '+ file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_MIN_FREQ_ON_AC=/ c#INTEL_GPU_MIN_FREQ_ON_AC=0" '+ file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_BAT=/ c#INTEL_GPU_MAX_FREQ_ON_BAT=0" '+ file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_MAX_FREQ_ON_AC=/ c#INTEL_GPU_MAX_FREQ_ON_AC=0" '+ file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_BAT=/ c#INTEL_GPU_BOOST_FREQ_ON_BAT=0" '+ file_equilibrado)
                    os.system('sed -i "/INTEL_GPU_BOOST_FREQ_ON_AC=/ c#INTEL_GPU_BOOST_FREQ_ON_AC=0" '+ file_equilibrado)  
                   
        if mode == '3':
            # Radeon integrated
            if subprocess.getstatusoutput('lscpu | grep -i model | grep -i Radeon')[0]== 0:
                print('Radeon graphics power profile: high')
                RADEON_POWER_PROFILE_ON_BAT='high'
                # Radeon changes
                os.system('sed -i "/RADEON_POWER_PROFILE_ON_BAT=/ c#RADEON_POWER_PROFILE_ON_BAT='+RADEON_POWER_PROFILE_ON_BAT+'" '+ file_equilibrado)
                os.system('sed -i "/RADEON_DPM_STATE_ON_BAT=/ c#RADEON_DPM_STATE_ON_BAT=0'+RADEON_DPM_STATE_ON_BAT+'" '+ file_equilibrado)
                os.system('sed -i "/RADEON_DPM_PERF_LEVEL_ON_BAT=/ c#RADEON_DPM_PERF_LEVEL_ON_BAT='+RADEON_DPM_PERF_LEVEL_ON_BAT+'" '+ file_ahorro)
            
            # Intel integrated
            elif subprocess.getstatusoutput('lspci | grep VGA | grep Intel')== 0:
                print('Intel graphics power profile: high')
                for i in range(len(freq_available)):
                    if(int(freq_available[i]) > 0 and int(freq_available[i]) < 600):
                        min_bat = int(freq_available[i])
                        min_ac = int(freq_available[i])
                        break
                #Si el valor que se busca no se encuentra, el boolean freqCorrecta pasará a False y por lo tanto no se realizará ninguna modificación respecto a gráficas Intel
                if min_bat == 0:
                    freqCorrecta = False
                if min_ac == 0:
                    freqCorrecta = False

                if int(freq_available[-1]) > 0 and freqCorrecta == True:
                    max_ac = int(freq_available[-1])
                    max_bat = int(freq_available[-1])
                if max_ac == 0:
                    freqCorrecta = False
                if max_bat == 0:
                    freqCorrecta = False

                if int(freq_available[-1]) > 0 and freqCorrecta == True:
                    boost_ac = int(freq_available[-1])
                    boost_bat = int(freq_available[-1])
                if boost_ac == 0:
                    freqCorrecta = False
                if boost_bat == 0:
                    freqCorrecta = False
                    
                #Si el boolean sigue en True querrá decir que se han obtenido valores para min, max y boost y se llamará al script para poder realizar las modificaciones
                if freqCorrecta == True:
                    update_config(file_max,'INTEL_GPU_MIN_FREQ_ON_BAT', str(min_bat))
                    update_config(file_max,'INTEL_GPU_MIN_FREQ_ON_AC', str(min_ac))
                    update_config(file_max,'INTEL_GPU_MAX_FREQ_ON_BAT', str(max_bat))
                    update_config(file_max,'INTEL_GPU_MAX_FREQ_ON_AC', str(max_ac))
                    update_config(file_max,'INTEL_GPU_BOOST_FREQ_ON_BAT', str(boost_bat))
                    update_config(file_max,'INTEL_GPU_BOOST_FREQ_ON_AC', str(boost_ac)) 

    return required_reboot

def brightness_settings(mode):
    
    print('[BRIGTHNESS SETTINS]')
    set_brightness = ''

    if mode == '1':
        if config.get('SETTINGS', 'saving_brightness_switch') == '1':
            set_brightness = config.get('SETTINGS', 'ahorro_brightness')
              
    elif mode == '2':
        if config.get('SETTINGS', 'balanced_brightness_switch') == '1':
            set_brightness = config.get('SETTINGS', 'equilibrado_brightness')   

    elif mode == '3':
        if config.get('SETTINGS', 'power_brightness_switch') == '1':
            set_brightness = config.get('SETTINGS', 'maxrendimiento_brightness')
    
    if config.get('CONFIGURATION', 'application_on') == '1':

        if set_brightness != '':

            if os.path.isdir("/sys/class/backlight"):
                for name in os.listdir("/sys/class/backlight"):
                    if os.path.isfile("/sys/class/backlight/"+ name +"/max_brightness") and os.path.isfile("/sys/class/backlight/"+ name +"/brightness"):
                        brilloMax = int(subprocess.getoutput("cat /sys/class/backlight/"+ name +"/max_brightness"))
                        brightness = int((brilloMax / 100) * int(set_brightness))
                        print('Setting Brightness (mode'+mode+')  to ' +str(brightness)+' <--> '+set_brightness+' % ... | Exit: '+str(subprocess.getstatusoutput('echo '+str(brightness)+' > /sys/class/backlight/'+name+'/brightness')[0]))

                        # CRONTAB EDIT
                        if not os.path.isfile("/var/spool/cron/crontabs/root"):
                            os.system('''cp /usr/share/slimbookbattery/src/root /var/spool/cron/crontabs/root
                                        chmod 600 /var/spool/cron/crontabs/root')
                                        chgrp crontab /var/spool/cron/crontabs/root''')
                        if subprocess.getstatusoutput('cat /var/spool/cron/crontabs/root | grep slimbookbattery')[0] == 0:
                            subprocess.getoutput('sed -i "/slimbookbattery/ c@reboot /usr/bin/slimbookbattery-pkexec autostart" /var/spool/cron/crontabs/root')
                            print('Crontab settings added')
                        else:
                            subprocess.getoutput("sed -i '$a @reboot /usr/bin/slimbookbattery-pkexec autostart' /var/spool/cron/crontabs/root")
                            print('Crontab settings added')
        else:
            # CRONTAB EDIT
            print('Brightness setting is off') 
            if not os.path.isfile("/var/spool/cron/crontabs/root"):
                os.system('''cp /usr/share/slimbookbattery/root /var/spool/cron/crontabs/root
                            chmod 600 /var/spool/cron/crontabs/root')
                            chgrp crontab /var/spool/cron/crontabs/root''')
            if os.system('cat /var/spool/cron/crontabs/root | grep slimbookbattery') == 0:
                os.system('sed -i "/slimbookbattery/ c#@reboot /usr/bin/slimbookbattery-pkexec autostart" /var/spool/cron/crontabs/root')
                print('Crontab settings commented')
    
    else: # Disabling crontab settings
        print('Application is off --> Restoring brightnes management') 
        if not os.path.isfile("/var/spool/cron/crontabs/root"):
            os.system('''cp /usr/share/slimbookbattery/root /var/spool/cron/crontabs/root
                        chmod 600 /var/spool/cron/crontabs/root')
                        chgrp crontab /var/spool/cron/crontabs/root''')
        if os.system('cat /var/spool/cron/crontabs/root | grep slimbookbattery') == 0:
            os.system('sed -i "/slimbookbattery/ c#@reboot /usr/bin/slimbookbattery-pkexec autostart" /var/spool/cron/crontabs/root')
            print('Crontab settings commented')        
            
def update_config(file, variable, value):
    
    # We change our variable: config.set(section, variable, value)
    call = subprocess.getoutput('cat '+file)
    patron = re.compile(variable+'\=(.*)')
    var_value = patron.search(call)[0]
    last_value = patron.search(call)[1]

    #print(last_value, value)

    if last_value != value:
        command = "sudo sed -i '/"+variable+"/ c"+variable+"="+value+"' "+file
        #print(command)
        if os.system(command) == 0:
            print("\n- Variable |"+variable+"| updated in "+file+", actual value: "+value)
        else:
            print('\n Sed command failed')
    else:
        print('Already set')



if __name__ == "__main__":
    #Se obtiene las variables que se le pasa desde el archivo /usr/share/slimbookface/slimbookface
    main(sys.argv)