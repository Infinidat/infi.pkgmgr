__import__("pkg_resources").declare_namespace(__name__)

from infi.pyutils.lazy import cached_method, cached_function, clear_cache

import logging # pylint: disable=W0403
logger = logging.getLogger()

WAIT_TIME = 120
QUERY_TIME = WAIT_TIME
INSTALL_TIME = 300

def execute_command(cmd, check_returncode=True, timeout=WAIT_TIME): # pragma: no cover
    from infi.execute import execute
    from os import environ
    logger.info("executing {}".format(cmd))
    env = environ.copy()
    env.pop('PYTHONPATH', 1)
    process = execute(cmd, env=env)
    process.wait(WAIT_TIME)
    logger.info("execution returned {}".format(process.get_returncode()))
    logger.debug("stdout: {}".format(process.get_stdout()))
    logger.debug("stderr: {}".format(process.get_stderr()))
    if check_returncode and process.get_returncode() != 0:
        raise RuntimeError("execution of {} failed. see log file for more details".format(cmd))
    return process

class PackageManager(object): # pylint: disable=R0922
    def install_package(self, package_name):
        raise NotImplementedError() # pragma: no cover

    def is_package_installed(self, package_name):
        raise NotImplementedError() # pragma: no cover

    def remove_package(self, package_name):
        raise NotImplementedError() # pragma: no cover

class UbuntuPackageManager(PackageManager):
    def install_package(self, package_name):
        cmd = "apt-get install -y {}".format(package_name).split()
        execute_command(cmd, timeout=INSTALL_TIME)

    def is_package_installed(self, package_name):
        cmd = "aptitude show {}".format(package_name).split()
        aptitude = execute_command(cmd, timeout=QUERY_TIME)
        return self._extract_state_from_aptitude_search_output(aptitude.get_stdout()) == "installed"

    def _extract_state_from_aptitude_search_output(self, string):
        import re
        pattern = "^State: (?P<state>[A-Za-z0-9_-]+)$"
        match = re.search(pattern, string, re.MULTILINE)
        if match is None:
            return ''
        return match.groupdict()['state']

    def remove_package(self, package_name):
        cmd = "apt-get remove -y {}".format(package_name).split()
        execute_command(cmd, timeout=INSTALL_TIME)

class RedHatPackageManager(PackageManager):
    def install_package(self, package_name):
        cmd = "yum install -y {}".format(package_name).split()
        execute_command(cmd, timeout=INSTALL_TIME)

    def is_package_installed(self, package_name):
        cmd = "rpm -q {}".format(package_name).split()
        info = execute_command(cmd, timeout=QUERY_TIME, check_returncode=False)
        if info.get_returncode() == 0 and 'not installed' not in info.get_stdout():
            return True
        if info.get_returncode() == 1 and 'package {} is not installed'.format(package_name) in info.get_stdout():
            return False
        raise RuntimeError("rpm -q returned unexpected results, see the log")

    def remove_package(self, package_name):
        cmd = "yum remove -y {}".format(package_name).split()
        execute_command(cmd, timeout=INSTALL_TIME)

class SusePackageManager(PackageManager):
    def install_package(self, package_name):
        cmd = "zypper --non-interactive --no-gpg-checks install --auto-agree-with-licenses {}".format(package_name).split()
        execute_command(cmd, timeout=INSTALL_TIME)

    def is_package_installed(self, package_name):
        cmd = "rpm -q {}".format(package_name).split()
        info = execute_command(cmd, timeout=QUERY_TIME, check_returncode=False)
        if info.get_returncode() == 0 and 'not installed' not in info.get_stdout():
            return True
        if info.get_returncode() == 1 and 'package {} is not installed'.format(package_name) in info.get_stdout():
            return False
        raise RuntimeError("rpm -q returned unexpected results, see the log")

    def remove_package(self, package_name):
        cmd = "zypper --non-interactive --no-gpg-checks remove {}".format(package_name).split()
        execute_command(cmd, timeout=INSTALL_TIME)

class SolarisPackageManager(PackageManager):
    def install_package(self, package_name):
        # There is no unified package repository for solaris
        raise NotImplementedError

    def is_package_installed(self, package_name):
        cmd = "pkginfo {}".format(package_name).split()
        info = execute_command(cmd, timeout=QUERY_TIME, check_returncode=False)
        if info.get_returncode() == 0 and 'not found' not in info.get_stderr():
            return True
        elif info.get_returncode() == 1 and 'ERROR: information for "{}" was not found'.format(package_name) in info.get_stderr():
            return False
        else:
            raise RuntimeError("pkginfo returned unexpected results, see the log")

    def remove_package(self, package_name):
        raise NotImplementedError
