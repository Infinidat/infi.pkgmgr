__import__("pkg_resources").declare_namespace(__name__)

from infi.pyutils.lazy import cached_method, cached_function, clear_cache
from infi.vendata.powertools.utils import execute_command

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
