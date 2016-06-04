"""
Tools for getting the configured PAC file URL out of the Windows Registry.
"""
import platform
from subprocess import check_output, CalledProcessError, STDOUT


REG_CMD = ['reg', 'query', 'HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings', '/v', 'AutoConfigURL']


def on_windows():
    """
    :return: `True` when running on Windows.
    :rtype: bool
    """
    return platform.system() == 'Windows'


def autoconfig_url_from_registry():
    """
    Get the PAC URL from the Windows Registry.
    This setting is visible as the "use automatic configuration script" field in
    Internet Options > Connection > LAN Settings.

    :return: The PAC URL from the registry, or None if the value isn't configured or available.
    :rtype: str|None
    :raises NotWindowsError: If called on a non-Windows platform.
    """
    if not on_windows():
        raise NotWindowsError()
    try:
        output = check_output(REG_CMD, stderr=STDOUT)
        return parse_reg_output(output)
    except CalledProcessError as e:
        if e.returncode == 1:
            # Assume that key wasn't found.
            return
        raise


class NotWindowsError(Exception):
    def __init__(self):
        super(NotWindowsError, self).__init__("Platform is not Windows.")


def parse_reg_output(value):
    """
    Parse out the value of the REG_SZ key as output from the `reg` command.

    :param value: bytestring output from `reg` that contains the value of `AutoConfigURL`.
    :returns: URL
    :rtype: str
    """
    decoded = value.decode('ascii')
    return decoded[decoded.find('REG_SZ') + 6:].strip()
