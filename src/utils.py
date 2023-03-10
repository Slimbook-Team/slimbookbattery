import getpass
import gettext
import os
from re import sub
import sys
import subprocess
import locale
import logging

from pkg_resources import parse_version as parse_version

def get_logger(logger_name, create_file=False):

        log = logging.getLogger(logger_name)
        log.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')

        if create_file:
            try:            
                fh = logging.FileHandler('/var/log/slimbookbattery.log')
            except PermissionError:
                log.critical(
                    'Cannot open log file /var/slimbookbattery.log, using /tmp/slimbookbattery.log')
                fh = logging.FileHandler('/tmp/slimbookbattery.log')
            if fh:
                fh.setLevel(level=logging.ERROR)
                fh.setFormatter(formatter)

            log.addHandler(fh)

        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(level=logging.ERROR)
        ch.setFormatter(formatter)
        log.addHandler(ch)
        return log 

logger = get_logger("utils.py", True)

PKG_MANAGERS = {
        "rpm": {
            "distros": [
                "fedora",
                "rhel",
            ],
            "install_command": "-i",
            "get_app_list_cmd": "-qa",
        },
        "zypper": {
            "distros": [
                "suse",
                "opensuse",
            ],
            "install_command": "in",
            "get_app_list_cmd": None,
        },
        "apt": {
            "distros": [
                "ubuntu",
                "debian",
                "elementary"
            ],
            "install_command": "install",
            "get_app_list_cmd": "list --installed",
        },
        "yum": {
            "distros": [
                "centos"
            ],
            "install_command": "install",
            "get_app_list_cmd": None,
        },
        "pacman": {
            "distros": [
                "manjaro",
                "arch",
            ],
            "install_command": "-S",
            "get_app_list_cmd": "-Q",
        }
    }

PACKAGES = {
        "linux-tools-$(uname -r)": {
            "rpm": "kernel-tools",
            "pacman": "linux-tools-meta",
            "apt": "linux-tools-$(uname -r)",
        },
    }

def get_user(from_file=None):
    try:
        user_name = getpass.getuser()
    except Exception:
        user_name = os.getlogin()

    if from_file and os.path.exists(from_file):
        exit_code, candidate = subprocess.getstatusoutput(
            f'cat {from_file} | tail -n 1 | cut -f 2 -d "@"')
        if exit_code != 0:
            user_name = candidate

    if user_name == 'root':
        if 'SUDO_USER' in os.environ and os.environ['SUDO_USER'] != 'root':
            user_name = os.environ['SUDO_USER']
        else:
            var = 10
            while var > 0:
                var -= 1
                user_name = subprocess.getoutput(
                    'last -wn1 | head -n 1 | cut -f 1 -d " "')
                logger.debug(f"Username: {user_name}")
                if user_name != 'reboot':
                    break
    return user_name

# Returns pkg_man, install_cmd, and package name if it is provided as an argument

def get_install_command(package_manager=None):
    pkg_man = package_manager or get_package_manager()
    if pkg_man:
        try:
            command = PKG_MANAGERS[pkg_man]['install_command']
            return command
        except Exception as e:
            logger.error("No distro install command found")
    return None

def get_package_manager():
    id, id_like = get_os_info()
    pkg_man = None
    if id:
        for pkg_man in PKG_MANAGERS:
            for distro in PKG_MANAGERS[pkg_man]['distros']:
                if distro == id:
                    return pkg_man
    else:
        logger.error('No distro id found')
    return None

def get_package_name(apt_package_name):
    PACKAGES = {
        "linux-tools-$(uname -r)": {
            "rpm": "kernel-tools",
            "pacman": "linux-tools-meta",
            "apt": "linux-tools-$(uname -r)",
        },
    }
    pkg_man = get_package_manager()
    
    for pkg_name in PACKAGES:
        if apt_package_name == pkg_name:
            for pkg_manager in PACKAGES[pkg_name]:
                if pkg_manager == pkg_man:
                    logger.info(PACKAGES[pkg_name][pkg_manager])
                    return PACKAGES[pkg_name][pkg_manager]

    logger.error(f"No package-name found for {apt_package_name}, in {pkg_man}")
    return None

def check_package_installed(package_name):
    pkg_name = get_package_name(package_name)
    if pkg_name:
        pkg_man = get_package_manager()
        if pkg_man:
            try:
                cmd = PKG_MANAGERS[pkg_man]['get_app_list_cmd']
                if subprocess.getstatusoutput(f"{pkg_man} {cmd} | grep {pkg_name}")[0] == 0:
                    return True
            except Exception:
                print(Exception)
                logger.error("Could not get list of installed apps.")
    return False
def get_os_info():
    subprocess.getstatusoutput('cat /etc/*-release')
    import csv
    OS_INFO = {}
    with open("/etc/os-release") as f:
        reader = csv.reader(f, delimiter="=")
        for row in reader:
            if row:
                OS_INFO[row[0]] = row[1]

    if OS_INFO['ID']:
        id = OS_INFO['ID']
        id_like = OS_INFO['ID_LIKE'] or None
    else:
        id = None
    return id, id_like


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
    if code == 0:
        res = res[res.find('TLP'):-1]
        version = res.split(' ')[1]
    else:
        version = '1.3'  # Most common
    try:
        if parse_version(version) >= parse_version('1.3'):
            file = '/etc/tlp.conf'
        else:
            file = '/etc/default/tlp'
    except Exception as ex:
        print(str(ex)+'\nTLP version not found, using TLP 1.3 config file.')
        file = '/etc/tlp.conf'
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
    process = subprocess.getoutput(f"{pkg_man} {cmd} | grep {pkg_name}")
    # If it finds a process, kills it
    if len(process.split('\n')) > 0:
        proc_list = process.split('\n')
        print('Processes: ', proc_list)
        for i in range(len(proc_list)):
            try:
                subprocess.getstatusoutput(f'kill -9 {proc_list[i]}')
            except:
                print('Killing process failed')
    if not os.path.isfile(path):
            return (1, 'Process launch path does not exist')
    if os.system(f'python3 {path} &') == 0:
        return (0, 'Process killed & launched')
