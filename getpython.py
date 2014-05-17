import os
import sys
import tempfile
import urllib2
import _winreg

def download(url, dest):
    with open(dest, 'wb') as msifile:
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

def find_exe(filename):
    for d in os.environ['PATH'].split(';'):
        path = os.path.join(d.strip(), filename)
        if os.path.exists(path):
            return path
    return None

def find_python_path():
    return find_exe('python.exe')

def check_install():
    return find_python_path() != None

def append_to_system_path(directory):
    key = _winreg.OpenKey(
        _winreg.HKEY_LOCAL_MACHINE, 
        r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 
        0, _winreg.KEY_ALL_ACCESS,
    )
    _winreg.SetValueEx(
        key, 'Path', 0, _winreg.REG_EXPAND_SZ, 
        os.environ['PATH'] + ';' + directory,
    )
    os.environ['PATH'] += ';' + directory

def get_system_drive():
    cmd_path = find_exe('cmd.exe')
    return os.path.splitdrive(cmd_path)[0]

force_install = True

if force_install or not check_install():
    msi_path = os.path.join(tempfile.gettempdir(), 'python-2.7.6.msi')
    msi_done_path = msi_path + '.download'
    
    if not os.path.exists(msi_path) or not os.path.exists(msi_done_path):
        print 'Downloading Python 2.7.6 installer ...'
        if os.path.exists(msi_done_path):
            os.remove(msi_done_path)
        download('https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi', msi_path)
        open(msi_done_path, 'w').close()
    
    print 'Installing Python ...'
    os.system(msi_path + ' /quiet /norestart')

    print 'Appending Python to the system PATH ...'
    append_to_system_path(os.path.join(get_system_drive(), 'Python27'))

    if not check_install():
        print 'Installation failed!'
        sys.exit(1)
