from optparse import OptionParser
import _winreg
import os
import sys
import tempfile
import urllib2

def parse_command_line():

    parser = OptionParser(
        usage = '%prog [options]'
    )
    
    parser.add_option(
        '-f', '--force-install', dest='force_install', default=False,
        help='force installation, even if Python is already on the system',
        action='store_true',
    )

    parser.add_option(
        '--msi-path', dest='msi_path', default=None,
        help='path to python installer MSI (by default, will download from www.python.org)',
        metavar='FILE',
    )

    parser.add_option(
        '--pip-path', dest='pip_install_path', default=None,
        help='path to get-pip.py (by default, will download from www.python.org)',
        metavar='FILE',
    )
    
    return parser.parse_args()

(options, args) = parse_command_line()

def download(url, dest):
    done_path = dest + '.download'

    if os.path.exists(dest) and os.path.exists(done_path):
        return

    with open(dest, 'wb') as msifile:
        if os.path.exists(done_path):
            os.remove(done_path)

        response = urllib2.urlopen(url)
        total_size = int(response.info().getheader('Content-Length').strip())
        byte_count = 0
    
        while True:
            chunk = response.read(8192)
            byte_count += len(chunk)
            msifile.write(chunk)
    
            if not chunk:
                break
    
            sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %  (
                byte_count,
                total_size, 
                100.0 * byte_count / total_size, 
            ))
    
        sys.stdout.write('\n')
        response.close()
        open(done_path, 'w').close()

def find_exe(filename):
    for d in os.environ['PATH'].split(';'):
        path = os.path.join(d.strip(), filename)
        if os.path.exists(path):
            return path
    return None

def find_python_path():
    return find_exe('python.exe')

def is_python_installed():
    return find_python_path() != None

def append_to_system_path(directory):
    key = _winreg.OpenKey(
        _winreg.HKEY_LOCAL_MACHINE, 
        r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 
        0, _winreg.KEY_ALL_ACCESS,
    )
    path = _winreg.QueryValueEx(key, 'Path')[0]
    paths = set(path.split(';'))
    paths.add(directory)
    path = ';'.join(paths)
    _winreg.SetValueEx(
        key, 'Path', 0, _winreg.REG_EXPAND_SZ, path,
    )
    os.environ['PATH'] += ';' + directory

def get_system_drive():
    cmd_path = find_exe('cmd.exe')
    return os.path.splitdrive(cmd_path)[0] + '\\'

if options.force_install or not is_python_installed():
    msi_path = None
    
    if options.msi_path:
        msi_path = options.msi_path
    else:
        msi_path = os.path.join(tempfile.gettempdir(), 'python-2.7.6.msi')
        print 'Downloading Python 2.7.6 installer ...'
        download('https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi', msi_path)
    
    print 'Installing Python ...'
    os.system(msi_path + ' /quiet /norestart')

    print 'Appending Python to the system PATH ...'
    append_to_system_path(os.path.join(get_system_drive(), 'Python27'))

    if not is_python_installed():
        print 'Installation failed!'
        sys.exit(1)

    pip_install_path = None

    if options.pip_install_path:
        pip_install_path = options.pip_install_path
    else:
        pip_install_path = os.path.join(tempfile.gettempdir(), 'get-pip.py')
        print 'Downloading pip install script ...'
        download('https://bootstrap.pypa.io/get-pip.py', pip_install_path)

    print 'Installing pip ...'
    os.system('python ' + pip_install_path)

    print 'Adding pip to the system PATH ...'
    append_to_system_path(os.path.join(get_system_drive(), r'Python27\Scripts'))

print 'Success!'
