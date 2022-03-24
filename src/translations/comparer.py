#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser, os, shutil, subprocess

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

files = {
    'preferences.po': 'slimbookbatterypreferences.template.po',
    'slimbookbattery.po':'slimbookbatteryindicator.template.po',
    'sudocommands.template.po':'sudocommands.template.po'
}

def create_dict(file):
    # Diccionario con los valores del archovo nuevo
    d = dict()
    with open(os.path.join(CURRENT_PATH, file), "r") as f:
        res = ''
        for line in f.readlines():
            
            if line.startswith('msgid'):
                res = res + line.strip()[line.find('"')+1: -1]
                
            elif line.startswith('msgstr') or line.startswith('#'):        
                if not res.startswith('Project') and len(res)>0:   
                    d[res] = ''
                res = ''
                pass
            else:
                res = res + line.strip()[line.find('"')+1: -1]

        # for item in d.items():
        #     print(item)
    return d
        
def create_copy_all():
    for dir in os.listdir(os.path.join(CURRENT_PATH)) :
        full_dir = os.path.join(CURRENT_PATH, dir, 'LC_MESSAGES')
        if os.path.isdir(full_dir):
            # Directorio idioma
            print(dir)
            trans_dir = os.path.join(full_dir, 'trans')
            new_trans_dir = os.path.join(full_dir, 'trans', 'new')
        
            if not os.path.exists(trans_dir):
                os.mkdir(trans_dir)    
            else:
                for f in os.listdir(trans_dir):
                    to_delete = os.path.join(trans_dir, f)             
                    try:
                        os.remove(to_delete)
                    except:
                        shutil.rmtree(to_delete)
                
            if not os.path.exists(new_trans_dir):
                    os.mkdir(new_trans_dir)
            else:
                for f in os.listdir(new_trans_dir):
                    to_delete = os.path.join(trans_dir, f)              
                    try:
                        os.remove(to_delete)
                    except:
                        shutil.rmtree(to_delete)
                        
            
                    
    # Now we have a folder with a copy of all translated files, to be used                  

            for file in os.listdir(full_dir):
                if file.endswith('.po'):
                    # Cada archivo .po en el dir de idioma
                    full_file = os.path.join(full_dir, file)
                    full_file = shutil.copy(full_file, trans_dir)

                    new_file = files.get(file) # **** Luego sera el mismo nombre de archivo en ambos directorios
                    full_new_file = os.path.join(CURRENT_PATH, new_file)
                    full_new_file = shutil.copy(full_new_file, new_trans_dir)
                    #print('\t', file, full_file, '\n\t', new_file, full_new_file)

def get_msgstr(line, lines):
    #print(line)
    pass

# file = 'preferences.po'
# dict = create_dict(files.get(file))

# #grep -n SEARCHTERM
# file = os.path.join(CURRENT_PATH, 'es', 'LC_MESSAGES', 'trans', file)

# with open(file, "r") as f:
#     lines = f.readlines()
#     for value in dict:

#         code, res = subprocess.getstatusoutput('grep -n "'+value+'" '+file)
        
#         if code == 0:
#             print('Found: '+res)
#             start_line = int(res.split(':')[0])
#             print(lines[start_line])
            
#             get_msgstr(start_line, lines)
            
#         else:
#             print('Not Found: '+value)



# Deletes all trans dirs
for dir in os.listdir(os.path.join(CURRENT_PATH)) :
        full_dir = os.path.join(CURRENT_PATH, dir, 'LC_MESSAGES')
        trans_dir = os.path.join(full_dir, 'trans')
        if os.path.isdir(full_dir):
            shutil.rmtree(trans_dir)