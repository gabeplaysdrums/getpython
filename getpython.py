from optparse import OptionParser
import _winreg
import os
import sys
import tempfile
import urllib2
import zipfile
import distutils.dir_util
import pkgutil

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
        '--python-installer-path', dest='python_installer_path', default=None,
        help='path to python installer MSI (by default, will download from www.python.org)',
        metavar='FILE',
    )

    parser.add_option(
        '--pip-installer-path', dest='pip_installer_path', default=None,
        help='path to get-pip.py (by default, will download from https://pypi.python.org/pypi/pip/)',
        metavar='FILE',
    )

    parser.add_option(
        '-p', '--install-package', dest='packages', default=[],
        help='install python package',
        metavar='PACKAGE',
        action='append',
    )

    parser.add_option(
        '--install-pywin32', dest='install_pywin32', default=False,
        help='install pywin32 libraries',
        action='store_true',
    )

    parser.add_option(
        '--pywin32-installer-path', dest='pywin32_installer_path', default=None,
        help='path to pywin32 installer (by default, will download from http://sourceforge.net/projects/pywin32)',
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

def is_python_installed():
    return find_exe('python.exe') != None

def is_pip_installed():
    return find_exe('pip.exe') != None

def is_pywin32_installed():
    mod_path = os.path.join(get_system_drive(), r'Python27\Lib\site-packages\win32\lib\pywintypes.py')
    return os.path.exists(mod_path)

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

def install_pywin32(pywin32_installer_path):
    """
    Manual silent install of pywin32
    (source: http://forums.arcgis.com/threads/33808-PyWin32-212.win32-py2.6-silent-install)

    """

    print 'Extracting pywin32 installer ...'
    extract_root = os.path.join(tempfile.gettempdir(), 'pywin32')

    if not os.path.exists(extract_root):
        os.makedirs(extract_root)

    z = zipfile.ZipFile(pywin32_installer_path)
    for f in z.namelist():
        if f.endswith('/'):
            os.makedirs(os.path.join(extract_root, f))
    z.extractall(extract_root)

    print 'Installing pywin32 ...'
    packages_root = os.path.join(get_system_drive(), r'Python27\Lib\site-packages')
    distutils.dir_util.copy_tree(os.path.join(extract_root, 'PLATLIB'), packages_root)

    os.system('python %s -install -silent' % (
        os.path.join(extract_root, r'SCRIPTS\pywin32_postinstall.py'),
    ))

if options.force_install or not is_python_installed():
    python_installer_path = None
    
    if options.python_installer_path:
        python_installer_path = options.python_installer_path
    else:
        python_installer_path = os.path.join(tempfile.gettempdir(), 'python-2.7.6.msi')
        print 'Downloading Python installer ...'
        download('https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi', python_installer_path)
    
    print 'Installing Python ...'
    os.system(python_installer_path + ' /quiet /norestart')

    print 'Appending Python to the system PATH ...'
    append_to_system_path(os.path.join(get_system_drive(), 'Python27'))

    if not is_python_installed():
        print 'Installation failed!'
        sys.exit(1)

if options.force_install or not is_pip_installed():
    pip_installer_path = None

    if options.pip_installer_path:
        pip_installer_path = options.pip_installer_path
    else:
        pip_installer_path = os.path.join(tempfile.gettempdir(), 'get-pip.py')
        print 'Downloading pip install script ...'
        download('https://bootstrap.pypa.io/get-pip.py', pip_installer_path)

    print 'Installing pip ...'
    os.system('python ' + pip_installer_path)

    print 'Adding pip to the system PATH ...'
    append_to_system_path(os.path.join(get_system_drive(), r'Python27\Scripts'))

if options.install_pywin32 and (options.force_install or not is_pywin32_installed()):
    pywin32_installer_path = None

    if options.pywin32_installer_path:
        pywin32_installer_path = options.pywin32_installer_path
    else:
        pywin32_installer_path = os.path.join(tempfile.gettempdir(), 'pywin32-219.win32-py2.7.exe')
        print 'Downloading pywin32 installer ...'
        download(
            'http://downloads.sourceforge.net/project/pywin32/pywin32/Build%20219/pywin32-219.win32-py2.7.exe?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fpywin32%2Ffiles%2Fpywin32%2FBuild%2520219%2F&ts=1401331200&use_mirror=iweb', 
            pywin32_installer_path
        )

    install_pywin32(pywin32_installer_path)

if options.packages:
    print 'Installing packages ...'
    os.system('pip install ' + ' '.join(options.packages))

print 'Success!'
