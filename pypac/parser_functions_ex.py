"""
Python implementation of JavaScript functions for Microsoft's IPv6 extensions.
For Python 2.7 compatibility, this doesn't use the ``ipaddress`` module
or the IPv6 ``socket`` functions that are not available in Python 2.7.

- Spec: https://learn.microsoft.com/en-us/windows/win32/winhttp/ipv6-extensions-to-navigator-auto-config-file-format
- De-facto API: https://bits.netbeans.org/dev/javadoc/org-netbeans-core-network/org/netbeans/core/network/proxy/pac/PacHelperMethodsMicrosoft.html
"""

# ruff: noqa: N802
import re
import socket
from requests.utils import address_in_network, is_ipv4_address


def getClientVersion():
    """
    :returns: WPAD engine version. Always "1.0".
    :rtype: str
    """
    return "1.0"


def sortIpAddressList(addrs):
    """
    Sort a list of IP addresses, with IPv6 addresses first, then IPv4 addresses.
    Follows the behaviour of Chrome and NetBeans.

    :param str|set addrs: IP addresses as semicolon-separated string or iterable.
    :returns: Sorted semicolon-separated string of IP addresses,
        or empty string if sorting failed.
    :rtype: str
    """
    if not addrs:
        return ""
    if isinstance(addrs, str):
        addrs = addrs.split(";")
    try:
        ipv6 = sorted((addr for addr in addrs if ":" in addr), key=lambda x: _parse_ipv6_to_hextets(x))
        ipv4 = sorted((addr for addr in addrs if ":" not in addr), key=lambda x: tuple(map(int, x.split("."))))
        return ";".join(ipv6 + ipv4)
    except ValueError:
        return ""


def myIpAddressEx():
    """
    :returns: All local IPv4 and IPv6 addresses as a semicolon-separated string.
        Entries are sorted by address family with IPv6 first, then sorted by address.
    :rtype: str
    """
    addrs = set()
    try:
        addrs.update(set(socket.gethostbyname_ex(socket.gethostname())[2]))
    except socket.gaierror:
        pass

    for host in (None, ""):  # These 2 hosts may return different addresses.
        try:
            results = socket.getaddrinfo(host, 0, 0)
        except socket.gaierror:
            continue
        for addr in results:
            if addr[0] in (socket.AF_INET6, socket.AF_INET):
                addrs.add(addr[4][0])

    return sortIpAddressList(addrs)


def dnsResolveEx(host):
    """
    :param str host: Hostname to resolve.
    :returns: List of resolved IP addresses as a semicolon-separated string.
    :rtype: str
    """
    try:
        return ";".join([addr[4][0] for addr in socket.getaddrinfo(host, 0)])
    except socket.gaierror:
        return ""


def isResolvableEx(host):
    """
    :param str host: Hostname to resolve.
    :returns: True if the hostname is resolvable, False otherwise.
    :rtype: bool
    """
    return dnsResolveEx(host) != ""


def _parse_ipv6_to_hextets(ipv6_str):
    """
    Converts an IPv6 address string to a list of 8 16-bit integers.
    Handles "::" expansion and also pads with zeros if fewer than 8 hextets
    are provided without "::" (common for network address part of a CIDR).
    """
    if ipv6_str == "::":  # Special case for the unspecified address
        return [0] * 8

    if "::" in ipv6_str:
        prefix_str, suffix_str = ipv6_str.split("::", 1)
        if "::" in suffix_str or suffix_str.startswith(":"):
            raise ValueError("Invalid compression syntax")
        prefix_hextets = [int(p, 16) for p in prefix_str.split(":") if p] if prefix_str else []
        suffix_hextets = [int(p, 16) for p in suffix_str.split(":") if p] if suffix_str else []

        num_present_hextets = len(prefix_hextets) + len(suffix_hextets)
        if num_present_hextets > 8:
            raise ValueError("Too many hextets")

        num_zeros_to_add = 8 - num_present_hextets
        hextets = prefix_hextets + [0] * num_zeros_to_add + suffix_hextets
    else:
        hextets = [int(p, 16) for p in ipv6_str.split(":")]
        if len(hextets) > 8:
            raise ValueError("Too many hextets")
        # If no "::" and less than 8 hextets, pad with zeros at the end.
        if len(hextets) < 8:
            hextets.extend([0] * (8 - len(hextets)))

    assert len(hextets) == 8
    for seg in hextets:
        if not (0 <= seg <= 0xFFFF):
            raise ValueError("Hextet out of range")
    return hextets


def _ipv6_addr_in_network(ipv6_addr_str, ipv6_prefix_str):
    """
    Checks if an IPv6 address string is within a given IPv6 prefix string.

    :param ipv6_addr_str: The IPv6 address string (e.g., "2001:db8:cafe::1").
    :param ipv6_prefix_str: The IPv6 prefix string (e.g., "2001:db8::/32").
    :return: True if the address is in the network, False otherwise.
    :raises ValueError: If inputs are malformed.
    """
    try:
        network_part_str, prefix_len_str = ipv6_prefix_str.split("/", 1)
        prefix_len = int(prefix_len_str)
    except ValueError:
        raise ValueError("Invalid IPv6 prefix format")

    if not (0 <= prefix_len <= 128):
        raise ValueError("IPv6 prefix length must be between 0 and 128")

    if prefix_len == 0:  # /0 prefix matches all addresses
        return True

    addr_hextets = _parse_ipv6_to_hextets(ipv6_addr_str)
    prefix_net_hextets = _parse_ipv6_to_hextets(network_part_str)

    bits_remaining_to_compare = prefix_len
    for i in range(8):  # Iterate through 8 hextets (16 bits each)
        if bits_remaining_to_compare == 0:
            break

        hextet_addr = addr_hextets[i]
        hextet_net = prefix_net_hextets[i]

        if bits_remaining_to_compare >= 16:
            # Compare all 16 bits of this hextet
            if hextet_addr != hextet_net:
                return False
            bits_remaining_to_compare -= 16
        else:
            # Compare partial hextet (most significant 'bits_remaining_to_compare' bits)
            # Create a mask for these most significant bits
            # e.g., if bits_remaining_to_compare = 8, mask is 0xFF00
            # e.g., if bits_remaining_to_compare = 1, mask is 0x8000
            mask = ((1 << bits_remaining_to_compare) - 1) << (16 - bits_remaining_to_compare)
            if (hextet_addr & mask) != (hextet_net & mask):
                return False
            bits_remaining_to_compare = 0  # All relevant bits for this prefix processed
            # No need to check further hextets as we've processed the last partial one
            break

    return True


def isInNetEx(addrs_or_hosts, patterns):
    """
    :param str addrs_or_hosts: Semicolon-separated string of IP addresses or hostnames.
        For example, "8.8.8.8;example.com;2001:db8::1".
    :param str patterns: Semicolon-separated string of patterns to match against.
        For example, "192.168.0.1/24;3ffe:8311:ffff/48".
    :return: True if any address or hostname matches any pattern.
    :rtype: bool
    """
    addrs_or_hosts = addrs_or_hosts.split(";")
    patterns = list(filter(lambda x: "/" in x, patterns.split(";")))  # skip unprefixed
    ipv4_patterns = list(filter(lambda x: "." in x, patterns))
    ipv6_patterns = list(filter(lambda x: ":" in x, patterns))

    for item in addrs_or_hosts:
        # If it isn't an IPv4 address and doesn't somewhat look like an IPv6 address, resolve it.
        if not is_ipv4_address(item) and not re.match(r"^[:0-9A-F]+$", item, re.I):
            addrs = dnsResolveEx(item).split(";")
        else:
            addrs = [item]

        for addr in filter(lambda x: x, addrs):
            if is_ipv4_address(addr):
                for pattern in ipv4_patterns:
                    try:
                        if address_in_network(addr, pattern):
                            return True
                    except ValueError:
                        continue
            else:  # IPv6
                for pattern in ipv6_patterns:
                    try:
                        if _ipv6_addr_in_network(addr, pattern):
                            return True
                    except ValueError:
                        continue

    return False


# Things to add to the scope of the JavaScript PAC file.
function_injections = {
    "getClientVersion": getClientVersion,
    "myIpAddressEx": myIpAddressEx,
    "sortIpAddressList": sortIpAddressList,
    "dnsResolveEx": dnsResolveEx,
    "isResolvableEx": isResolvableEx,
    "isInNetEx": isInNetEx,
}
