"""
Tools for getting the configured PAC file URL out of the OS settings.
"""
import platform
from sys import version_info


if version_info[0] == 2:
    from urlparse import urlparse  # noqa
    from urllib import unquote  # noqa
else:
    from urllib.parse import urlparse, unquote  # noqa


#: True if running on Windows.
ON_WINDOWS = platform.system() == "Windows"

#: True if running on macOS/OSX.
ON_DARWIN = platform.system() == "Darwin"

if ON_WINDOWS:
    try:
        import winreg
    except ImportError:
        import _winreg as winreg  # PY2.

if ON_DARWIN:
    import SystemConfiguration


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
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"
        ) as key:
            return winreg.QueryValueEx(key, "AutoConfigURL")[0]
    except WindowsError:
        return  # Key or value not found.


def autoconfig_url_from_preferences():
    """
    Get the PAC ``AutoConfigURL`` value from the macOS System Preferences.
    This setting is visible as the "URL" field in
    System Preferences > Network > Advanced... > Proxies > Automatic Proxy Configuration.

    :return: The value from the registry, or None if the value isn't configured or available.
        Note that it may be local filesystem path instead of a URL.
    :rtype: str|None
    :raises NotDarwinError: If called on a non-macOS/OSX platform.
    """
    if not ON_DARWIN:
        raise NotDarwinError()

    try:
        config = SystemConfiguration.SCDynamicStoreCopyProxies(None)
    except AttributeError:
        return  # Key or value not found.

    if all(
        (
            "ProxyAutoConfigEnable" in config,
            "ProxyAutoConfigURLString" in config,
            not config.get("ProxyAutoDiscoveryEnable", 0),
        )
    ):
        # Only return a value if it is enabled, not empty, and auto discovery is disabled.
        return str(config["ProxyAutoConfigURLString"])


def file_url_to_local_path(file_url):
    """
    Parse a ``AutoConfigURL`` value with ``file://`` scheme into a usable local filesystem path.

    :param file_url: Must start with ``file://``.
    :return: A local filesystem path. It might not exist.
    """
    parts = urlparse(file_url)
    path = unquote(parts.path)
    if path.startswith("/") and not path.startswith("//"):
        if ON_DARWIN:
            return path
        if len(parts.netloc) == 2 and parts.netloc[1] == ":":  # Drive letter and colon.
            return parts.netloc + path
        return "C:" + path  # Assume C drive if it's just a path starting with /.
    if len(path) > 2 and path[1] == ":":
        return path


class NotWindowsError(Exception):
    def __init__(self):
        super(NotWindowsError, self).__init__("Platform is not Windows.")


class NotDarwinError(Exception):
    def __init__(self):
        super(NotDarwinError, self).__init__("Platform is not macOS/OSX.")
