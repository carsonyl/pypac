import socket

from pypac.parser_functions import myIpAddress
from pypac.parser_functions_ex import getClientVersion, myIpAddressEx


def test_getClientVersion():
    assert getClientVersion() == "1.0"


def test_myIpAddressEx(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (socket.AF_INET6, None, None, None, ("2001:db8::1", 0, 0, 0)),
            (socket.AF_INET, None, None, None, ("192.168.1.1", 0)),
            (socket.AF_INET6, None, None, None, ("fe80::1", 0, 0, 0)),
            (socket.AF_INET, None, None, None, ("10.0.0.1", 0)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    result = myIpAddressEx()
    assert result == "2001:db8::1;fe80::1;192.168.1.1;10.0.0.1"


def test_myIpAddressEx_live():
    result = myIpAddressEx()
    assert result
    result = result.split(";")
    local_ipv4 = myIpAddress()
    if local_ipv4:
        assert local_ipv4 in result
