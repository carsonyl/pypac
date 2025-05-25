"""
Python implementation of JavaScript functions for Microsoft's IPv6 extensions.

See https://learn.microsoft.com/en-us/windows/win32/winhttp/ipv6-extensions-to-navigator-auto-config-file-format
"""

# ruff: noqa: N802
import socket


def getClientVersion():
    """
    :returns: WPAD engine version. Always "1.0".
    :rtype: str
    """
    return "1.0"


def myIpAddressEx():
    """
    :returns: All local IPv4 and IPv6 addresses as a semicolon-separated string.
        Entries are sorted by address family with IPv6 first, then sorted by address.
    :rtype: str
    """
    ipv6 = []
    ipv4 = []
    for addr in socket.getaddrinfo("", 0, 0):
        if addr[0] == socket.AF_INET6:
            ipv6.append(addr[4][0])
        elif addr[0] == socket.AF_INET:
            ipv4.append(addr[4][0])
    return ";".join(ipv6 + ipv4)  # Assume that getaddrinfo() returns sorted addresses.


def sortIpAddressList(addrs):
    """
    Sort a list of IP addresses, with IPv6 addresses first, then IPv4 addresses.
    :param str addrs: Semicolon-separated string of IP addresses.
    :returns: Sorted semicolon-separated string of IP addresses,
        or empty string if sorting failed.
    :rtype: str
    """
    if not addrs:
        return ""
    addrs = addrs.split(";")
    try:
        # FIXME: Handle IPv6 :: address expansion
        ipv6 = sorted(
            (addr for addr in addrs if ":" in addr),
            key=lambda x: tuple(map(lambda i: int(i, 16) if i else 0, x.split(":"))),
        )
        ipv4 = sorted((addr for addr in addrs if ":" not in addr), key=lambda x: tuple(map(int, x.split("."))))
        return ";".join(ipv6 + ipv4)
    except ValueError:
        return ""


# Things to add to the scope of the JavaScript PAC file.
function_injections = {
    "getClientVersion": getClientVersion,
    "myIpAddressEx": myIpAddressEx,
    "sortIpAddressList": sortIpAddressList,
}
