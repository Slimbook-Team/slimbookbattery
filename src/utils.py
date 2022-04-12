import getpass
import gettext
import os
import subprocess
import locale

from pkg_resources import parse_version as parse_version

def get_user(from_file=None):
    try:
        user_name = getpass.getuser()
    except Exception:
        user_name = os.getlogin()

    if from_file and os.path.exists(from_file):
        exit_code, candidate = subprocess.getstatusoutput('cat {} | tail -n 1 | cut -f 2 -d "@"'.format(from_file))
        if exit_code != 0:
            user_name = candidate

    if user_name == 'root':
        if 'SUDO_USER' in os.environ and os.environ['SUDO_USER'] != 'root':
            user_name = os.environ['SUDO_USER']
        else:
            user_name = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

    return user_name

def get_languages():
    languages = ['en']
    try:
        user_environ = locale.getlocale()[0]
        for lang in ["en", "es", "it", "pt", "gl"]:
            if user_environ.find(lang) >= 0:
                languages = [lang]
                break
    except Exception:
        pass
    return languages

def get_tlp_conf_file():
    
    code, res = subprocess.getstatusoutput('tlp-stat --config | grep "TLP "')
    if code==0:
        res = res[res.find('TLP'):-1]
        version=res.split(' ')[1]
    else :
        version='1.3' # Most common    

    try:
        if parse_version(version)>= parse_version('1.3'):
            file='/etc/tlp.conf'
        else:
            file='/etc/default/tlp'
    except Exception as ex:
        print(str(ex)+'\nTLP version not found, using TLP 1.3 config file.')
        file='/etc/tlp.conf'
    return file, version

def get_version(v):
    return parse_version(v)

def load_translation(filename):
    current_path = os.path.dirname(os.path.realpath(__file__))
    languages = get_languages()
    return gettext.translation(
        filename,
        os.path.join(current_path, 'translations'),
        languages=languages,
        fallback=True
    ).gettext

def get_display_resolution():
    dimensions = subprocess.getoutput("xdpyinfo | grep 'dimensions:'")
    dimensions = dimensions.split()
    dimensions = dimensions[1]
    dimensions = dimensions.split('x')

    return dimensions

def reboot_process(process_name, path):
    process = subprocess.getoutput('pgrep -f ' + process_name)
    # If it finds a process, kills it
    if len(process.split('\n')) > 0:
        proc_list = process.split('\n')
        print('Processes: ', proc_list)
        for i in range(len(proc_list)):
            try:
                subprocess.getstatusoutput('kill -9 ' + proc_list[i])
            except:
                print('Killing process failed')
    if os.path.isfile(path):
        if os.system('python3 {} &'.format(path)) == 0:
            return (0, 'Process killed & launched')
    else:
        return (1, 'Process launch path does not exist')
   
