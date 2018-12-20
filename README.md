Overview
========

A simple wrapper for some Linux package managers.
The distributions currently supported are:
* Ubuntu (via apt-get)
* Redhat (via yum)
* SUSE (via zypper)
* Solaris (via pkginfo)

Usage
-----

Here is an example usage to install the package `sg3-utils` if it is not
already installed:
```python
from infi.pkgmgr import get_package_manager
pkgmgr = get_package_manager()
name = 'sg3-utils'
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