"""
Tools for getting the configured PAC file URL out of the Windows Registry.
"""
import platform
from sys import version_info


if version_info[0] == 2:
    from urlparse import urlparse  # noqa
    from urllib import unquote  # noqa
else:
    from urllib.parse import urlparse, unquote  # noqa


#: True if running on Windows.
ON_WINDOWS = platform.system() == 'Windows'

if ON_WINDOWS:
    try:
        import winreg
    except ImportError:
        import _winreg as winreg  # PY2.


def autoconfig_url_from_registry():
    """
    Get the PAC ``AutoConfigURL`` value from the Windows Registry.
    This setting is visible as the "use automatic configuration script" field in
    Internet Options > Connection > LAN Settings.

    :return: The value from the registry, or None if the value isn't configured or available.
        Note that it may be local filesystem path instead of a URL.
    :rtype: str|None
    :raises NotWindowsError: If called on a non-Windows platform.
    """
    if not ON_WINDOWS:
        raise NotWindowsError()

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            return winreg.QueryValueEx(key, 'AutoConfigURL')[0]
    except WindowsError:
        return  # Key or value not found.


def file_url_to_local_path(file_url):
    """
    Parse a ``AutoConfigURL`` value with ``file://`` scheme into a usable local filesystem path.

    :param file_url: Must start with ``file://``.
    :return: A local filesystem path. It might not exist.
    """
    parts = urlparse(file_url)
    path = unquote(parts.path)
    if path.startswith('/') and not path.startswith('//'):
        if len(parts.netloc) == 2 and parts.netloc[1] == ':':  # Drive letter and colon.
            return parts.netloc + path
        return 'C:' + path  # Assume C drive if it's just a path starting with /.
    if len(path) > 2 and path[1] == ':':
        return path


class NotWindowsError(Exception):
    def __init__(self):
        super(NotWindowsError, self).__init__("Platform is not Windows.")
