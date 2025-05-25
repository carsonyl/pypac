"""
Python implementation of JavaScript functions for Microsoft's IPv6 extensions.

See https://learn.microsoft.com/en-us/windows/win32/winhttp/ipv6-extensions-to-navigator-auto-config-file-format
"""
# ruff: noqa: N802


def getClientVersion():
    """
    :returns: WPAD engine version. Always "1.0".
    :rtype: str
    """
    return "1.0"


# Things to add to the scope of the JavaScript PAC file.
function_injections = {
    "getClientVersion": getClientVersion,
}
