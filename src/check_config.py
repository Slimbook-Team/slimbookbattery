import os
import sys
import subprocess
import configparser

USERNAME = subprocess.getstatusoutput("logname")

if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd '+USERNAME[1]) == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)

CURRPATH = os.path.dirname(os.path.realpath(__file__))

default = CURRPATH+'/slimbookbattery.conf'
config_file = HOMEDIR+'/.config/slimbookbattery/slimbookbattery.conf'

print('Config check executed as '+USER_NAME)

def main(args):
  
    check()
    check2()
    if subprocess.getoutput('whoami') == 'root':
        print('Giving permisions ...')
        os.system('sudo chmod 777 -R '+HOMEDIR+'/.config/slimbookbattery')
        print('Done')
    else:
        print('Done')

def check(): # Args will be like --> command_name value
    if os.path.isfile(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        vars = subprocess.getoutput('cat '+default).split('\n')
        #print(str(vars))
        incidences = False

        section = ''
        for var in vars:
            
            if var.find('=') != -1:
                # We get the line, then the variable name, then we remove spaces at the start or the end
                value = var.split('=')[1].strip()
                var = var.split('=')[0].strip()
                try:
                    config[section][var]
                except:
                    incidences = True
                    print('Not found: '+var)
                    try:
                        config.set(section,var,value)
                    except:
                        config.add_section(section)
                        print('Section added')
                        config.set(section,var,value)
                    
            else:
                if var.startswith('[') and var.endswith(']'):                
                    section = var[1:len(var)-1]
                    print('Checking section: '+section+'...')
        
        if incidences:
            try:
                configfile = open(config_file, 'w')
                config.write(configfile)
                configfile.close()
                print('Incidences corrected.')
            except:
                print('Incidences could not be corrected.')
        else:
            print('Incidences not found.')
    else:
        print('Creating config file ...')
        os.system('''mkdir -p '''+HOMEDIR+'''/.config/slimbookbattery/ && cp '''+default+''' '''+config_file)

def check2():
    # Slimbookbattery tlp conf files
    incidences = False

    files = ['ahorrodeenergia', 'equilibrado', 'maximorendimiento']
    for file in files:
        if not os.path.isfile(HOMEDIR+'/.config/slimbookbattery/custom/'+file):
            incidences = True
    for file in files:
        if not os.path.isfile(HOMEDIR+'/.config/slimbookbattery/default/'+file):
            incidences = True

    if incidences:
        print('Creating default an custom files ...')
        os.system('''cp -r /usr/share/slimbookbattery/custom '''+HOMEDIR+'''/.config/slimbookbattery/
                    cp -r /usr/share/slimbookbattery/default '''+HOMEDIR+'''/.config/slimbookbattery/
                    ''')

main(sys.argv)