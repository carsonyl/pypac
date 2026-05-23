"""Internal helpers."""

import sys

ON_WINDOWS = sys.platform.startswith("win")
ON_DARWIN = sys.platform == "darwin"
ON_PY3 = sys.version_info[0] >= 3


def is_ipv4_address(string_ip):
    """
    :rtype: bool
    """
    import socket

    try:
        socket.inet_aton(string_ip)
    except OSError:
        return False
    return True
