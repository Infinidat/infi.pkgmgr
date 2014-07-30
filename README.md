Overview
========

A simple wrapper for some Linux package managers.
The distributions currently supported are:
* Ubuntu (via apt-get)
* Redhat (via yum)

Usage
-----

The first example, on ubuntu:
```python
from infi.pkgmgr import UbuntuPackageManager
pkgmgr = UbuntuPackageManager()
name = 'sg3-utils'
pkgmgr.install_package(name) if not pkgmgr.is_package_installed(name) else None
```

Now, on redhat:
```python
from infi.pkgmgr import RedHatPackageManager
pkgmgr = RedHatPackageManager()
name = 'sg3_utils'
pkgmgr.install_package(name) if not pkgmgr.is_package_installed(name) else None
```

Checking out the code
=====================

Run the following:

    easy_install -U infi.projector
    projector devenv build
