"""
Tools for getting the configured PAC file URL out of the Windows Registry.
"""
import platform

if platform.system() == 'Windows':
    try:
        import winreg
    except ImportError:
        import _winreg as winreg  # PY2.


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
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            return winreg.QueryValueEx(key, 'AutoConfigURL')[0]
    except WindowsError:
        return  # Key or value not found.


class NotWindowsError(Exception):
    def __init__(self):
        super(NotWindowsError, self).__init__("Platform is not Windows.")
