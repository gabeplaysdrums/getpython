import urllib2
import sys
import tempfile
import os

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

msi_path = os.path.join(tempfile.gettempdir(), 'python-2.7.6.msi')
msi_done_path = msi_path + '.download'

if not os.path.exists(msi_path) or not os.path.exists(msi_done_path):
    print 'Downloading Python 2.7.6 installer ...'
    if os.path.exists(msi_done_path):
        os.remove(msi_done_path)
    download('https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi', msi_path)
    open(msi_done_path, 'w').close()
