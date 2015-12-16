from . import UbuntuPackageManager, RedHatPackageManager, SolarisPackageManager, RpmMixin
from infi import unittest

from infi.run_as_root import RootPermissions
from infi.pyutils.contexts import contextmanager

from infi import pkgmgr
#pylint: disable-all


def get_platform_name(): # pragma: no cover
    from platform import system
    name = system().lower().replace('-', '_')
    return name

def get_distribution(): # pragma: no cover
    """:returns: bunch with the following keys: distname, version, id
    """
    from munch import Munch
    from platform import linux_distribution
    distname, version, _id = linux_distribution()
    # distname in ['Red Hat Enterprise Linux Server', 'Ubuntu']
    distname = ''.join(distname.split()[:2]).lower()
    return Munch(distname=distname, version=version, id=_id.lower())

class TestOnUbuntu(unittest.TestCase):
    def _running_on_ubuntu(self):
        return get_platform_name() == "linux" and get_distribution().distname == "ubuntu"

    def setUp(self):
        super(TestOnUbuntu, self).setUp()
        self._should_skip()

    def _should_skip(self):
        if not self._running_on_ubuntu():
            raise self.skipTest("This test runs only on ubuntu")
        if not RootPermissions().is_root():
            raise self.skipTest("This test must run with root permissions")

    def test_sg3_utils(self):
        self._check_package("sg3-utils", "/usr/bin/sg_inq")

    def _check_package(self, package_name, executable_name):
        pkgmgr = UbuntuPackageManager()
        is_installed_before = self._is_package_seems_to_be_installed(package_name, executable_name)
        self.assertEqual(pkgmgr.is_package_installed(package_name), is_installed_before)
        # Do the opposite
        pkgmgr.install_package(package_name) if not is_installed_before else pkgmgr.remove_package(package_name)
        self.assertNotEqual(pkgmgr.is_package_installed(package_name), is_installed_before)

    def _is_package_seems_to_be_installed(self, package_name, executable_name):
        from os.path import exists
        return exists(executable_name)

class TestOnRedHat(unittest.TestCase):
    def _running_on_ubuntu(self):
        return get_platform_name() == "linux" and get_distribution().distname == "redhat"

    def setUp(self):
        super(TestOnRedHat, self).setUp()
        self._should_skip()

    def _should_skip(self):
        if not self._running_on_ubuntu():
            raise self.skipTest("This test runs only on ubuntu")
        if not RootPermissions().is_root():
            raise self.skipTest("This test must run with root permissions")

    def test_sg3_utils(self):
        self._check_package("sg3_utils", "/usr/bin/sg_inq")

    def _check_package(self, package_name, executable_name):
        pkgmgr = RedHatPackageManager()
        is_installed_before = self._is_package_seems_to_be_installed(package_name, executable_name)
        self.assertEqual(pkgmgr.is_package_installed(package_name), is_installed_before)
        # Do the opposite
        pkgmgr.install_package(package_name) if not is_installed_before else pkgmgr.remove_package(package_name)
        self.assertNotEqual(pkgmgr.is_package_installed(package_name), is_installed_before)

    def _is_package_seems_to_be_installed(self, package_name, executable_name):
        from os.path import exists
        return exists(executable_name)

from mock import patch

class Output(object):
    def __init__(self, returncode=0, stdout='', stderr=''):
        super(Output, self).__init__()
        self._returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def get_stdout(self):
        return self._stdout

    def get_stderr(self):
        return self._stderr

    def get_returncode(self):
        return self._returncode

    def wait(self, timeout=None):
        pass

class TestUbuntuMock(TestOnUbuntu):
    def _should_skip(self):
        pass

    def _aptitude_show(self):
        from textwrap import dedent
        return Output(stdout=dedent("""
                                    Package: sg3-utils
                                    State: {}
                                    Automatically installed: no
                                    Version: 1.30-1
                                    Priority: optional
                                    Section: admin
                                    """.format("installed" if self._installed else "not installed")))

    def _apt_get(self):
        self._installed = True
        return Output()

    @contextmanager
    def _apply_patches(self):
        with patch("infi.execute.execute") as execute:
            def side_effect(*args, **kwargs):
                command = args[0]
                if "aptitude" in command:
                    return self._aptitude_show()
                elif "apt-get" in command:
                    return self._apt_get()
                raise NotImplementedError()
            execute.side_effect = side_effect
            yield

    def test_sg3_utils(self):
        with self._apply_patches():
            super(TestUbuntuMock, self).test_sg3_utils()
        pass

    def setUp(self):
        self._installed = False

    def _is_package_seems_to_be_installed(self, package_name, executable_name):
        return self._installed

class TestRedHatMock(TestOnRedHat):
    def _should_skip(self):
        pass

    def _rpm_query(self):
        from textwrap import dedent
        return Output(stdout='sg3_utils-1.25-5.el5' if self._installed else 'package sg3_utils is not installed',
                      returncode=0 if self._installed else 1)

    def _yum_install(self):
        self._installed = True
        return Output()

    @contextmanager
    def _apply_patches(self):
        with patch("infi.execute.execute") as execute:
            def side_effect(*args, **kwargs):
                command = args[0]
                if "-q" in command:
                    return self._rpm_query()
                elif "install" in command:
                    return self._yum_install()
                raise NotImplementedError()
            execute.side_effect = side_effect
            yield

    def test_sg3_utils(self):
        with self._apply_patches():
            super(TestRedHatMock, self).test_sg3_utils()
        pass

    def setUp(self):
        self._installed = False

    def _is_package_seems_to_be_installed(self, package_name, executable_name):
        return self._installed

class test_package_versioning(unittest.TestCase):

    Solaris_v1 = """   VERSION:  6.0.100.000,REV=08.01.2012.09.00"""
    Solaris_v2 = """   VERSION:  5.14.2.5"""
    Ubuntu_v1 = """Version: 0.4.9-3ubuntu7.2"""
    Ubuntu_v2 = """Version: 1:1.2.8.dfsg-1ubuntu1"""
    rpm_v1 = """4.8-7.el7"""
    rpm_v2 = """18.168.6.1-34.el7"""
    def test_solaris_versioning_v1(self):
        with patch.object(pkgmgr , 'execute_command') as patched:
            patched().get_stdout.return_value = self.Solaris_v1
            result = SolarisPackageManager().get_installed_version(self.Solaris_v1)
            self.assertEqual(result,{'version':'6.0.100.000', 'revision':'08.01.2012.09.00'})

    def test_solaris_versioning_v2(self):
        with patch.object(pkgmgr , 'execute_command') as patched:
            patched().get_stdout.return_value = self.Solaris_v2
            result = SolarisPackageManager().get_installed_version(self.Solaris_v2)
            self.assertEqual(result,{'version':'5.14.2.5'})

    def test_ubuntu_versioning_v1(self):
        with patch.object(pkgmgr , 'execute_command') as patched:
            patched().get_stdout.return_value = self.Ubuntu_v1
            result = UbuntuPackageManager().get_installed_version(self.Ubuntu_v1)
            self.assertEqual(result,{'version':'0.4.9-3ubuntu7.2'})

    def test_ubuntu_versioning_v2(self):
        with patch.object(pkgmgr , 'execute_command') as patched:
            patched().get_stdout.return_value = self.Ubuntu_v2
            result = UbuntuPackageManager().get_installed_version(self.Ubuntu_v2)
            self.assertEqual(result,{'version':'1:1.2.8.dfsg-1ubuntu1'})

    def test_rpm_versioning_v1(self):
        with patch.object(pkgmgr , 'execute_command') as patched:
            patched().get_stdout.return_value = self.rpm_v1
            patched().get_returncode.return_value = 0
            result = RpmMixin().get_installed_version(self.rpm_v1)
            self.assertEqual(result,{'version':'4.8-7.el7'})

    def test_rpm_versioning_v2(self):
        with patch.object(pkgmgr , 'execute_command') as patched:
            patched().get_stdout.return_value = self.rpm_v2
            patched().get_returncode.return_value = 0
            result = RpmMixin().get_installed_version(self.rpm_v2)
            self.assertEqual(result,{'version':'18.168.6.1-34.el7'})

class GeneralTest(unittest.TestCase):
    def _is_solaris(self):
        from infi.os_info import get_platform_string
        return get_platform_string().split('-')[0] == 'solaris'

    def test_get_package_manager(self):
        package_manager = pkgmgr.get_package_manager()
        package_to_check = 'python'
        if self._is_solaris():
            package_to_check = 'CSW' + package_to_check
        self.assertTrue(package_manager.is_package_installed(package_to_check))
