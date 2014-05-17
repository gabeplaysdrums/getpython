import urllib2
import sys

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

download('https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi', '/tmp/python-2.7.6.msi')
