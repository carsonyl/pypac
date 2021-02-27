import pytest
import warnings

from pypac.parser import MalformedPacError, PACFile, parse_pac_value, proxy_url


class TestPacFile(object):
    """
    Tests for acceptance and rejection of PAC file JavaScript.
    """

    @pytest.mark.parametrize(
        "value",
        [
            "",
            " ",
            "<html>",
            "foo bar",
            "var x =",
            "var x = 1;",
            "function() foo(bar) { return 0; }",
        ],
    )
    def test_malformed_pac_files(self, value):
        with pytest.raises(MalformedPacError):
            PACFile(value)

    @pytest.mark.parametrize(
        "pac_js",
        [
            'function FindProxyForURL(url, host) { return "DIRECT"; }',
            'function FindProxyForURL(url, host, bar) { return "DIRECT"; }',
            'function FindProxyForURL(url) { return "DIRECT"; }',
        ],
    )
    def test_valid_js_function_signatures(self, pac_js):
        pac = PACFile(pac_js)
        assert pac.find_proxy_for_url("/", "example.com") == "DIRECT"

    @pytest.mark.parametrize(
        "pac_js",
        [
            "function FindProxyForURL(url, host) { return __builtins__; }",
            "function FindProxyForURL(url, host) { return shExpMatch.__class__.__class__; }",
        ],
    )
    def test_builtins_undefined(self, pac_js):
        with pytest.raises(MalformedPacError):
            PACFile(pac_js)

    def test_pac_callstack_limit(self):
        """
        Try to load a PAC file that hits the Duktape call stack limit.
        """
        pac_js = 'function FindProxyForURL(url, host) {function b() {a();} function a() {b();}; a(); return "DIRECT";}'
        with pytest.raises(MalformedPacError) as e:
            PACFile(pac_js)
        assert "callstack limit" in str(e.value)


dummy_js = 'function FindProxyForURL(url, host) {return %s ? "DIRECT" : "PROXY 0.0.0.0:80";}'


class TestFunctionsInPacParser(object):
    """
    Call the Python functions that were added to the JavaScript scope.
    This is mostly coverage for catching problems handling PyJs* class arguments.
    """

    def test_shExpMatch(self):
        parser = PACFile(dummy_js % 'shExpMatch(host, "*.example.com")')
        assert parser.find_proxy_for_url("/", "www.example.com") == "DIRECT"
        assert parser.find_proxy_for_url("/", "www.example.org") == "PROXY 0.0.0.0:80"

    def test_dnsDomainIs(self):
        parser = PACFile(dummy_js % 'dnsDomainIs(host, "example.com")')
        assert parser.find_proxy_for_url("/", "www.example.com") == "DIRECT"

    def test_isResolvable(self):
        parser = PACFile(dummy_js % "isResolvable(host)")
        assert parser.find_proxy_for_url("/", "www.google.com") == "DIRECT"
        assert parser.find_proxy_for_url("/", "bogus.domain.local") != "DIRECT"

    def test_isInNet(self):
        parser = PACFile(dummy_js % 'isInNet(host, "0.0.0.0", "0.0.0.0")')
        assert parser.find_proxy_for_url("/", "www.google.com") == "DIRECT"

    def test_localHostOrDomainIs(self):
        parser = PACFile(dummy_js % 'localHostOrDomainIs(host, "www.netscape.com")')
        assert parser.find_proxy_for_url("/", "www") == "DIRECT"

    def test_myIpAddress(self):
        js = 'function FindProxyForURL(url, host) {return "PROXY " + myIpAddress() + ":80"; }'
        parser = PACFile(js)
        assert parser.find_proxy_for_url("/", "www.example.com") is not None

    def test_dnsResolve(self):
        js = 'function FindProxyForURL(url, host) {return "PROXY " + dnsResolve(host) + ":80"; }'
        parser = PACFile(js)
        assert parser.find_proxy_for_url("/", "www.google.com") is not None

    def test_dnsResolve_propagation(self):
        """
        dnsResolve must return an empty string now we use dukpy, otherwise
        None value causes dukpy error as it propagates
        """
        parser = PACFile(dummy_js % 'isInNet(dnsResolve(host), "10.1.1.0", "255.255.255.0")')
        assert parser.find_proxy_for_url("$%$", "$%$") == "PROXY 0.0.0.0:80"

    def test_dnsDomainLevels(self):
        parser = PACFile(dummy_js % "dnsDomainLevels(host)")
        assert parser.find_proxy_for_url("/", "google.com") == "DIRECT"
        assert parser.find_proxy_for_url("/", "foobar") != "DIRECT"

    def test_isPlainHostName(self):
        parser = PACFile(dummy_js % "isPlainHostName(host)")
        assert parser.find_proxy_for_url("/", "google.com") != "DIRECT"
        assert parser.find_proxy_for_url("/", "foobar") == "DIRECT"

    @pytest.mark.parametrize(
        "func_body",
        [
            'weekdayRange("MON"); weekdayRange("MON","FRI");',
            'timeRange(12); timeRange(12,30,40,12,30,45,"GMT");',
            'dateRange(3); dateRange(1,"MAY",15,"JUN"); dateRange(1,"JAN",2016,2,"JUN",2016,"GMT");',
        ],
    )
    def test_temporal_functions(self, func_body):
        js = 'function FindProxyForURL(url, host) { %s return "DIRECT"; }' % func_body
        assert PACFile(js).find_proxy_for_url("/", "foo") == "DIRECT"


class TestFindProxyForURLOutputParsing(object):
    """
    Tests parsing of the outputs of the FindProxyForURL() function.
    """

    @pytest.mark.parametrize(
        "pac_value,expected_result",
        [
            ("DIRECT", "DIRECT"),
            ("direct", "DIRECT"),
            ("proxy foo", "http://foo"),
            ("PROXY foo:8080", "http://foo:8080"),
            ("SOCKS foo:8080", "socks5://foo:8080"),
        ],
    )
    def test_parse_single_value(self, pac_value, expected_result):
        assert parse_pac_value(pac_value) == [expected_result]
        assert proxy_url(pac_value) == expected_result

    def test_multiple(self):
        assert parse_pac_value("PROXY foo:8080; DIRECT") == ["http://foo:8080", "DIRECT"]

    @pytest.mark.parametrize(
        "bad_value",
        [
            "foo bar",
            "PROXY foo bar",
            "",
            ";",
            "example.local:8080",
        ],
    )
    def test_skip_invalid(self, bad_value):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            retval = "PROXY foo:8080; {}; DIRECT".format(bad_value)
            assert parse_pac_value(retval) == ["http://foo:8080", "DIRECT"]

    def test_empty(self):
        assert parse_pac_value("") == []
