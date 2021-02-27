import pytest
from requests.auth import HTTPProxyAuth

from pypac.parser import PACFile, proxy_url
from pypac.resolver import ProxyResolver, add_proxy_auth, ProxyConfigExhaustedError

mock_proxy_auth = HTTPProxyAuth("user", "pwd")
arbitrary_url = "http://example.org"


def _get_resolver(js_func_return_value, proxy_auth=None):
    """Get a ProxyResolver for a PAC that always returns the given value."""
    pac = PACFile('function FindProxyForURL(url, host) { return "%s"; }' % js_func_return_value)
    return ProxyResolver(pac, proxy_auth=proxy_auth)


@pytest.mark.parametrize(
    "pac_value",
    [
        "DIRECT",
        "PROXY foo:8080",
    ],
)
def test_single_pac_value(pac_value):
    res = _get_resolver(pac_value)
    assert res.get_proxies(arbitrary_url) == [proxy_url(pac_value)]
    assert res.get_proxy(arbitrary_url) == proxy_url(pac_value)


def test_proxy_failover():
    res = _get_resolver("PROXY first:8080; PROXY second:8080; DIRECT")
    assert res.get_proxy(arbitrary_url) == "http://first:8080"
    res.ban_proxy("http://first:8080")
    assert res.get_proxy(arbitrary_url) == "http://second:8080"
    res.ban_proxy("http://second:8080")
    assert res.get_proxy(arbitrary_url) == "DIRECT"


def test_proxy_failover_no_fallback():
    res = _get_resolver("PROXY first:8080")
    res.ban_proxy("http://first:8080")
    assert res.get_proxy("http://example.com") is None


@pytest.mark.parametrize(
    "proxy_value,auth_obj,expected_result",
    [
        ("DIRECT", mock_proxy_auth, "DIRECT"),
        ("http://foo:8080", mock_proxy_auth, "http://user:pwd@foo:8080"),
        ("socks5://foo:8080", mock_proxy_auth, "socks5://user:pwd@foo:8080"),
        ("http://foo:8080", HTTPProxyAuth("u$er", "p@ss:"), "http://u%24er:p%40ss%3A@foo:8080"),
    ],
)
def test_add_proxy_auth(proxy_value, auth_obj, expected_result):
    assert add_proxy_auth(proxy_value, auth_obj) == expected_result


def test_resolver_add_proxy_auth():
    res = _get_resolver("PROXY foo:8080", mock_proxy_auth)
    assert res.get_proxy(arbitrary_url) == "http://user:pwd@foo:8080"


def test_get_proxy_for_requests():
    res = _get_resolver("DIRECT")
    assert res.get_proxy_for_requests(arbitrary_url) == {"http": None, "https": None}

    res = _get_resolver("PROXY foo:8080")
    assert res.get_proxy_for_requests(arbitrary_url) == {
        "http": "http://foo:8080",
        "https": "http://foo:8080",
    }
    res.ban_proxy("http://foo:8080")
    with pytest.raises(ProxyConfigExhaustedError):
        res.get_proxy_for_requests(arbitrary_url)


def test_url_host_port_excluded():
    res = ProxyResolver(
        PACFile(
            'function FindProxyForURL(url, host) { return host.indexOf(" ") == -1 ? "PROXY PASS:80" : "PROXY FAIL:80"; }'
        )
    )
    for url in ("http://foo/bar", "http://foo:80/bar"):
        assert res.get_proxy(url) == "http://PASS:80"
