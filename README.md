getpython
=========

An application -- written in Python -- that installs Python on a Windows machine that doesn't have Python.  Yes, you read that correctly.

It takes care of:

* downloading the correct Python 2.7 installer from [python.org](http://python.org)
* installing Python in unattended mode
* downloading and installing [pip](http://www.pip-installer.org/) package manager
* adding Python and pip to the system PATH
* installing any additional python packages you specify on the command line

Example Usage
-------------
    Install Python, pip, pywin32, django, and south:
    getpython.exe --install-pywin32 -p django -p south
    
    Show usage:
    getpython.exe -h

Building
--------

Building **getpython** requires a Windows machine with Python installed.

1. Install [py2exe](http://py2exe.org) (`pip install py2exe`)
2. `python setup.py py2exe`

