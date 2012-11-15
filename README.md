Overview
========

A simple wrapper for some Linux package managers.
The distributions currently supported are:
* Ubutnu (via apt-get)
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

This project uses buildout and infi-projector, and git to generate setup.py and __version__.py.
In order to generate these, first get infi-projector:

    easy_install infi.projector

    and then run in the project directory:

        projector devenv build
