from __future__ import print_function
import pytest
from mock import patch

from pypac.wpad import proxy_urls_from_dns


@pytest.mark.parametrize('bad_host', [' ', '.', '.foo', 'bar.'])
def test_bad_host(bad_host):
    assert proxy_urls_from_dns(bad_host) == []


def test_this_host():
    with patch('socket.getfqdn', return_value='foo.example.local'):
        search_urls = proxy_urls_from_dns()
        assert len(search_urls) == 2
        for url in search_urls:
            assert url.startswith('http://wpad.')
            assert url.endswith('/wpad.dat')


@pytest.mark.parametrize('host_fqdn,expected_wpad,description', [
    ('carson-pc', [], 'no FQDN'),
    ('carson-pc.local', ['http://wpad.local/wpad.dat'], 'dot local'),
    ('pc.corp.local', ['http://wpad.corp.local/wpad.dat', 'http://wpad.local/wpad.dat'], 'unrecognized TLD'),
    ('pc.corp.example.com', ['http://wpad.corp.example.com/wpad.dat', 'http://wpad.example.com/wpad.dat'], 'dot com'),
    ('pc.example.org.uk', ['http://wpad.example.org.uk/wpad.dat'], 'org uk'),
])
def test_host_fqdn(host_fqdn, expected_wpad, description):
    print(description)
    assert proxy_urls_from_dns(host_fqdn) == expected_wpad
