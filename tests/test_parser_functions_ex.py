import socket

import pytest

from pypac.parser_functions import myIpAddress
from pypac.parser_functions_ex import (
    getClientVersion,
    myIpAddressEx,
    sortIpAddressList,
    dnsResolveEx,
    _parse_ipv6_to_hextets,
    _ipv6_addr_in_network,
    isInNetEx,
)


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


@pytest.mark.parametrize(
    "addresses, expected",
    [
        ("", ""),
        ("192.168.0.1", "192.168.0.1"),
        ("8.8.8.8;192.168.0.1", "8.8.8.8;192.168.0.1"),
        ("2001:db8::1", "2001:db8::1"),
        ("192.168.0.1;2001:db8::1", "2001:db8::1;192.168.0.1"),
        ("2001:xyz::1;a.b.c.d", ""),
    ],
)
def test_sortIpAddressList(addresses, expected):
    assert sortIpAddressList(addresses) == expected


def test_dnsResolveEx():
    assert dnsResolveEx("google.ca") != ""


@pytest.mark.parametrize(
    "ipv6_str, expected",
    [
        ("::", [0, 0, 0, 0, 0, 0, 0, 0]),
        ("2001:db8::", [8193, 3512, 0, 0, 0, 0, 0, 0]),
        ("2001:db8::1", [8193, 3512, 0, 0, 0, 0, 0, 1]),
        ("2001:db8:0:0:0:0:0:1", [8193, 3512, 0, 0, 0, 0, 0, 1]),
        ("::1", [0, 0, 0, 0, 0, 0, 0, 1]),
        ("2001:db8:1234:5678:9abc:def0:1234:5678", [8193, 3512, 4660, 22136, 39612, 57072, 4660, 22136]),
    ],
)
def test_ipv6_parse(ipv6_str, expected):
    assert _parse_ipv6_to_hextets(ipv6_str) == expected


@pytest.mark.parametrize(
    "ipv6_str",
    [
        "2001:db8:::1",
        "2001:db8:12345::",
        "2001:db8::g",
        "2001:db8::1::",
        "2001:db8:0:0:0:0:0:0:1",
    ],
)
def test_ipv6_parse_reject(ipv6_str):
    with pytest.raises(ValueError):
        _parse_ipv6_to_hextets(ipv6_str)


@pytest.mark.parametrize(
    "ipv6_addr, ipv6_prefix, expected",
    [
        ("2001:db8::1", "2001:db8::/32", True),
        ("2001:db8:abcd::1", "2001:db8::/32", True),
        ("2001:db9::1", "2001:db8::/32", False),
        ("2001:db8::1", "2001:db8::/128", False),
        ("2001:db8::2", "2001:db8::/128", False),
        ("::1", "::/0", True),
        ("2001:db8::1", "::/0", True),
        ("2001:db8::1", "2001:db8::/0", True),
        ("2001:db8::1", "2001:db8::/1", True),
        ("8000::1", "2001:db8::/1", False),
    ],
)
def test_ipv6_address_matches_prefix(ipv6_addr, ipv6_prefix, expected):
    assert _ipv6_addr_in_network(ipv6_addr, ipv6_prefix) == expected


@pytest.mark.parametrize(
    "ipv6_addr, ipv6_prefix",
    [
        ("2001:db8::1", "2001:db8::/129"),
        ("2001:db8::1", "invalid-prefix"),
        ("invalid-ip", "2001:db8::/32"),
    ],
)
def test_ipv6_address_matches_prefix_reject(ipv6_addr, ipv6_prefix):
    with pytest.raises(ValueError):
        _ipv6_addr_in_network(ipv6_addr, ipv6_prefix)


@pytest.mark.parametrize(
    "addrs_or_hosts, patterns, expected",
    [
        ("8.8.8.8", "8.8.8.0/24", True),
        ("8.8.8.8", "1.1.1.1/24;1.1.1.1;8.8.8.0/24", True),
        ("8.8.8.8;example.com", "8.8.8.0/24", True),
        ("example.com", "8.8.8.0/24", True),
        ("2001:db8::1", "2001:db8::/32", True),
        ("2001:db8::1;example.com", "2001:db8::/32", True),
        ("example.com", "2001:db8::/32", False),
        ("8.8.8.8;2001:db8::1", "8.8.8.0/24;2001:db8::/32", True),
        ("", "8.8.8.0/24", False),
        ("8.8.8.8", "", False),
        ("invalid-host", "8.8.8.0/24", False),
    ],
)
def test_isInNetEx(addrs_or_hosts, patterns, expected, monkeypatch):
    def fake_dns_resolve_ex(host):
        if host == "example.com":
            return "8.8.8.8"
        return ""

    monkeypatch.setattr("pypac.parser_functions_ex.dnsResolveEx", fake_dns_resolve_ex)
    assert isInNetEx(addrs_or_hosts, patterns) == expected
