Overview
========

A simple wrapper for some Linux package managers.
The distributions currently supported are:
* Ubuntu (via apt-get)
* Redhat (via yum)

Usage
-----

On Ubuntu:
```python
from infi.pkgmgr import UbuntuPackageManager
pkgmgr = UbuntuPackageManager()
name = 'sg3-utils'
if not pkgmgr.is_package_installed(name):
    pkgmgr.install_package(name)
```

On RedHat:
```python
from infi.pkgmgr import RedHatPackageManager
pkgmgr = RedHatPackageManager()
name = 'sg3_utils'
if not pkgmgr.is_package_installed(name):
    pkgmgr.install_package(name)
```

Checking out the code
=====================

To run this code from the repository for development purposes, run the following:

    easy_install -U infi.projector
    projector devenv build

Python 3
========
Python 3 support is experimental at this stage.