import socket
from datetime import datetime

import pytest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch  # noqa

from pypac.parser_functions import (
    alert,
    dateRange,
    dnsDomainIs,
    dnsDomainLevels,
    dnsResolve,
    isInNet,
    isPlainHostName,
    isResolvable,
    localHostOrDomainIs,
    myIpAddress,
    shExpMatch,
    timeRange,
    weekdayRange,
)


@pytest.mark.parametrize(
    "host,domain,expected_value",
    [
        ("www.netscape.com", ".netscape.com", True),
        ("www.netscape.com", "NETSCAPE.com", True),
        ("www", ".netscape.com", False),
        ("www.mcom.com", ".netscape.com", False),
    ],
)
def test_dnsDomainIs(host, domain, expected_value):
    assert dnsDomainIs(host, domain) == expected_value


@pytest.mark.parametrize(
    "host,expected_value",
    [
        ("www.google.com", True),
        ("bogus.domain.foobar", False),
    ],
)
def test_isResolvable(host, expected_value):
    assert isResolvable(host) == expected_value


@pytest.mark.parametrize(
    "host,pattern,mask,expected_value",
    [
        ("198.95.249.79", "198.95.249.79", "255.255.255.255", True),
        ("198.95.6.8", "198.95.0.0", "255.255.0.0", True),
        ("192.168.1.100", "192.168.2.0", "255.255.255.0", False),
        ("google.com", "0.0.0.0", "0.0.0.0", True),
        ("google.com", "google.com", "foo", False),
        (False, False, False, False),
    ],
)
def test_isInNet(host, pattern, mask, expected_value):
    assert isInNet(host, pattern, mask) == expected_value


@pytest.mark.parametrize(
    "host,hostdom,expected_value",
    [
        ("www.netscape.com", "www.netscape.com", True),
        ("www", "www.netscape.com", True),
        ("www.mcom.com", "www.netscape.com", False),
        ("home.netscape.com", "www.netscape.com", False),
    ],
)
def test_localHostOrDomainIs(host, hostdom, expected_value):
    assert localHostOrDomainIs(host, hostdom) == expected_value


def test_myIpAddress():
    hostname = socket.gethostname()
    try:
        socket.gethostbyname(hostname)
    except socket.gaierror as e:
        print("Could not resolve hostname {}: {}".format(hostname, e))
    assert myIpAddress().count(".") == 3


def test_dnsResolve():
    assert dnsResolve("google.com").count(".") == 3
    assert dnsResolve("bogus.domain.foobar") == ""


@pytest.mark.parametrize(
    "host,expected_levels",
    [
        ("www", 0),
        ("www.netscape.com", 2),
    ],
)
def test_dnsDomainLevels(host, expected_levels):
    assert dnsDomainLevels(host) == expected_levels


@pytest.mark.parametrize(
    "host,expected_value",
    [
        ("www", True),
        ("www.netscape.com", False),
    ],
)
def test_isPlainHostName(host, expected_value):
    assert isPlainHostName(host) == expected_value


@pytest.mark.parametrize(
    "url,pattern,expected_value",
    [
        ("http://home.netscape.com/people/ari/index.html", "*/ari/*", True),
        ("http://home.netscape.com/people/montulli/index.html", "*/ari/*", False),
    ],
)
def test_shExpMatch(url, pattern, expected_value):
    assert shExpMatch(url, pattern) == expected_value


@pytest.mark.parametrize(
    "args,expected_value",
    [
        (["MON", "FRI"], True),
        (["SAT"], False),
        (["SAT", "GMT"], False),
        (["FRI", "GMT"], True),
        (["FRI", "MON"], True),
    ],
)
def test_weekdayRange(args, expected_value):
    with patch("pypac.parser_functions._now", return_value=datetime(2016, 6, 3)):
        assert weekdayRange(*args) == expected_value


@pytest.mark.parametrize(
    "args,expected_value",
    [
        ([3], True),
        ([3, "GMT"], True),
        ([2016], True),
        ([2016, 2017], True),
        ([2015, 2016], True),
        ([2014, 2015], False),
        ([1, 15], True),
        ([15, 30], False),
        (["JUN"], True),
        (["MAY", "JUL"], True),
        ([1, "MAY", 15, "JUN"], True),
        ([5, "JUN", 15, "JUN"], False),
        (["JUN", 2016, "JUN", 2017], True),
        ([1, "JAN", 2016, 5, "JUN", 2016], True),
        ([1, "JAN", 2016, 2, "JUN", 2016], False),
        (["foo"], False),
    ],
)
def test_dateRange(args, expected_value):
    with patch("pypac.parser_functions._now", return_value=datetime(2016, 6, 3)):
        assert dateRange(*args) == expected_value


@pytest.mark.parametrize(
    "args,expected_value",
    [
        ([12], True),
        ([12, "GMT"], True),
        ([12, 13], True),
        ([11, 12], False),  # End hour is exclusive.
        ([12, 15, 12, 45], True),
        ([12, 30, 15, 12, 30, 45], True),
        ([12, 30, 40, 12, 30, 45], False),
    ],
)
def test_timeRange(args, expected_value):
    with patch("pypac.parser_functions._now", return_value=datetime(2016, 6, 3, 12, 30, 30)):
        assert timeRange(*args) == expected_value


def test_alert():
    alert("foo")
