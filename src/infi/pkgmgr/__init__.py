__import__("pkg_resources").declare_namespace(__name__)

from infi.pyutils.lazy import cached_method, cached_function, clear_cache

import logging # pylint: disable=W0403
logger = logging.getLogger()

def execute_command(cmd, check_returncode=True): # pragma: no cover
    from infi.execute import execute
    from os import environ
    logger.info("executing {}".format(cmd))
    env = environ.copy()
    env.pop('PYTHONPATH', 1)
    process = execute(cmd, env=env)
    process.wait()
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
        execute_command(cmd)

    def is_package_installed(self, package_name):
        cmd = "aptitude show {}".format(package_name).split()
        aptitude = execute_command(cmd)
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
        execute_command(cmd)

class RedHatPackageManager(PackageManager):
    def install_package(self, package_name):
        cmd = "yum install -y {}".format(package_name).split()
        execute_command(cmd)

    def is_package_installed(self, package_name):
        cmd = "yum info {}".format(package_name).split()
        info = execute_command(cmd)
        return self._extract_repo_name_from_info(info.get_stdout()) == "installed"

    def _extract_repo_name_from_info(self, string):
        import re
        pattern = "^Repo\s+: (?P<repo>[A-Za-z0-9_-]+)$"
        match = re.search(pattern, string, re.MULTILINE)
        if match is None:
            return ''
        return match.groupdict()['repo']

    def remove_package(self, package_name):
        cmd = "yum remove -y {}".format(package_name).split()
        execute_command(cmd)
