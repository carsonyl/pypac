import os
import pytest
import requests
from requests.auth import HTTPProxyAuth
from requests.exceptions import ProxyError, ConnectTimeout
from mock import patch, Mock, ANY, call
from requests.utils import select_proxy
from tempfile import mkstemp

from pypac.api import get_pac, collect_pac_urls, download_pac, PACSession, pac_context_for_url
from pypac.parser import PACFile, MalformedPacError
from pypac.resolver import proxy_parameter_for_requests

proxy_pac_js_tpl = 'function FindProxyForURL(url, host) { return "%s"; }'
direct_pac_js = proxy_pac_js_tpl % 'DIRECT'
valid_pac_headers = {'content-type': 'application/x-ns-proxy-autoconfig'}
arbitrary_url = 'http://example.org'
arbitrary_pac_url = arbitrary_url + '/proxy.pac'


def _patch_download_pac(return_value):
    return patch('pypac.api.download_pac', return_value=return_value)


def _patch_request_base(return_value=None, side_effect=None):
    return patch('requests.Session.request', return_value=return_value, side_effect=side_effect)


class TestApiFunctions(object):
    def test_get_pac_via_url(self):
        with _patch_download_pac(None):
            assert get_pac(url=arbitrary_pac_url) is None
        with _patch_download_pac(direct_pac_js):
            assert isinstance(get_pac(url=arbitrary_pac_url), PACFile)

    def test_get_pac_via_js(self):
        assert isinstance(get_pac(js=direct_pac_js), PACFile)

    def test_get_pac_autodetect(self):
        with _patch_download_pac(None):
            assert get_pac() is None
        with _patch_download_pac(direct_pac_js):
            assert isinstance(get_pac(), PACFile)

    def test_collect_pac_urls(self):
        with patch('pypac.api.ON_WINDOWS', return_value=True), \
             patch('socket.getfqdn', return_value='host.dns.local'):
            with patch('pypac.api.autoconfig_url_from_registry', return_value='http://foo.bar/proxy.pac'):
                assert collect_pac_urls() == [
                    'http://foo.bar/proxy.pac',
                    'http://wpad.dns.local/wpad.dat',
                    'http://wpad.local/wpad.dat',
                ]
            with patch('pypac.api.autoconfig_url_from_registry', return_value=r'C:\foo'):
                assert collect_pac_urls() == [
                    'http://wpad.dns.local/wpad.dat',
                    'http://wpad.local/wpad.dat',
                ]

    def test_download_pac_timeout(self):
        assert download_pac([arbitrary_pac_url], timeout=0.001) is None

    def test_download_pac_not_ok(self):
        mock_resp_not_ok = Mock(ok=False, headers=valid_pac_headers, text=direct_pac_js)
        with _patch_request_base(mock_resp_not_ok):
            assert download_pac([arbitrary_pac_url]) is None

    @pytest.mark.parametrize('headers,allowed_content_types,expected_value', [
        (valid_pac_headers, None, direct_pac_js),
        ({'content-type': 'text/plain'}, None, None),
        ({'content-type': 'text/plain'}, ['text/plain'], direct_pac_js)
    ])
    def test_download_pac_content_type(self, headers, allowed_content_types, expected_value):
        """Test acceptance/rejection of obtained PAC based on Content-Type header."""
        mock_pac_response = Mock(spec=requests.Response, ok=True, headers=headers, text=direct_pac_js)
        with _patch_request_base(mock_pac_response):
            result = download_pac([arbitrary_pac_url], allowed_content_types=allowed_content_types)
            assert result == expected_value

    def test_registry_filesystem_path(self):
        """
        The AutoConfigURL from the Windows Registry can also be a filesystem path.
        Test that this works, but local PAC files with invalid contents raise an error.
        """
        handle, fs_pac_path = mkstemp()
        os.close(handle)
        try:
            with patch('pypac.api.ON_WINDOWS', return_value=True), \
                 patch('pypac.api.autoconfig_url_from_registry', return_value=fs_pac_path):
                with pytest.raises(MalformedPacError):
                    get_pac(from_os_settings=True)

                with open(fs_pac_path, 'w') as f:
                    f.write(proxy_pac_js_tpl % 'DIRECT')
                assert isinstance(get_pac(from_os_settings=True), PACFile)
        finally:
            os.remove(fs_pac_path)


proxy_pac_js = proxy_pac_js_tpl % 'PROXY fake.local:8080; DIRECT'
fake_proxy_url = 'http://fake.local:8080'
fake_proxies_requests_arg = proxy_parameter_for_requests(fake_proxy_url)


def _patch_get_pac(return_value):
    return patch('pypac.api.get_pac', return_value=return_value)


def get_call(url, proxy):
    return call('GET', url, proxies=proxy_parameter_for_requests(proxy) if proxy else proxy,
                allow_redirects=ANY)


class TestRequests(object):
    """Test the behaviour of the Requests library that PyPAC expects."""

    @pytest.mark.parametrize('proxy_host', ['0.0.0.0', '127.0.0.1', 'unreachable.local', 'localhost'])
    def test_unreachable_proxy(self, proxy_host):
        session = requests.Session()
        with pytest.raises(ProxyError):
            session.get(arbitrary_url, proxies=proxy_parameter_for_requests('http://' + proxy_host))

    @pytest.mark.xfail(os.environ.get('TRAVIS', '').lower() == 'true', reason="Travis actively refuses localhost.")
    def test_timeout_proxy(self):
        # Travis can refuse quickly, and trigger ProxyError instead.
        session = requests.Session()
        with pytest.raises(ConnectTimeout):
            session.get(arbitrary_url, timeout=0.001, proxies=proxy_parameter_for_requests('http://localhost'))

    @pytest.mark.parametrize('request_url,expected_proxies,expected_proxy_selection', [
        ('http://a.local/x.html', {}, None),
        ('http://fooa.local/x.html', {}, None),  # Shady.
        ('http://foo.b.local/x.html', {}, None),
        ('http://foob.local/x.html', {'http': 'http://env', 'no': 'a.local, .b.local'}, 'http://env'),
        ('http://c.local/x.html', {'http': 'http://env', 'no': 'a.local, .b.local'}, 'http://env'),
    ])
    def test_environment_proxies(self, monkeypatch, request_url, expected_proxies, expected_proxy_selection):
        """Test usage of proxy settings from environment variables, including host exclusions using `NO_PROXY`."""
        monkeypatch.setenv('HTTP_PROXY', 'http://env')
        monkeypatch.setenv('NO_PROXY', 'a.local, .b.local')
        sess = requests.Session()
        settings = sess.merge_environment_settings(request_url, {}, False, False, False)
        assert settings['proxies'] == expected_proxies
        assert select_proxy(request_url, settings['proxies']) == expected_proxy_selection

    # @pytest.mark.parametrize('input_proxies,expected_proxy_selection', [
    #     ({'http': 'http://http'}, 'http://env'),
    #     ({'http://exact': 'http://override'}, 'http://override'),
    #     ({'all://exact': 'http://override'}, 'http://override'),
    # ])
    # def test_environment_all_proxy(self, monkeypatch, input_proxies, expected_proxy_selection):
    #     """When `ALL_PROXY` is defined, it takes precedence over other scheme-only proxy definitions.
    #     For Requests > 2.10.0."""
    #     monkeypatch.setenv('ALL_PROXY', 'http://env')
    #     sess = requests.Session()
    #     settings = sess.merge_environment_settings(arbitrary_url, input_proxies, False, False, False)
    #     proxies = {'all': 'http://env'}
    #     proxies.update(input_proxies)
    #     assert settings['proxies'] == proxies
    #     assert select_proxy(arbitrary_url, settings['proxies']) == expected_proxy_selection

    def test_override_env_proxy_and_go_direct(self, monkeypatch):
        """Ensure that it's possible to ignore environment proxy settings for a request."""
        monkeypatch.setenv('HTTP_PROXY', 'http://env')
        sess = requests.Session()
        settings = sess.merge_environment_settings(arbitrary_url, {'http': None}, False, False, False)
        assert settings['proxies'] == {}  # requests.session.merge_setting removes entries with None value.
        assert not select_proxy(arbitrary_url, settings['proxies'])

    def test_supercede_environment_settings(self, monkeypatch):
        monkeypatch.setenv('HTTP_PROXY', 'http://env')
        sess = requests.Session()
        settings = sess.merge_environment_settings(arbitrary_url, {'http': 'http://other'}, False, False, False)
        assert settings['proxies'] == {'http': 'http://other'}
        assert select_proxy(arbitrary_url, settings['proxies']) == 'http://other'


class TestPACSession(object):
    def test_default_behaviour_no_pac_found(self):
        sess = PACSession()
        mock_ok = Mock(spec=requests.Response, status_code=204)
        with _patch_get_pac(None), \
             _patch_request_base(mock_ok) as request:
            resp = sess.get(arbitrary_url)
            assert resp.status_code == 204
            request.assert_called_with('GET', arbitrary_url, proxies=None, allow_redirects=ANY)

    def test_no_pac_but_call_get_pac_twice(self):
        with _patch_get_pac(None):
            sess = PACSession()
            for _ in range(2):
                assert sess.get_pac() is None

    def test_default_behaviour_pac_found(self):
        sess = PACSession()
        mock_ok = Mock(spec=requests.Response, status_code=204)
        with _patch_get_pac(PACFile(proxy_pac_js)), \
             _patch_request_base(mock_ok) as request:
            assert sess.get(arbitrary_url).status_code == 204
            request.assert_called_with('GET', arbitrary_url,
                                       proxies=fake_proxies_requests_arg,
                                       allow_redirects=ANY)

    def test_pac_from_constructor(self):
        sess = PACSession(pac=PACFile(direct_pac_js))
        for _ in range(2):
            assert sess.get_pac() is not None

    def test_pac_override_using_request_proxies_parameter(self):
        sess = PACSession()
        mock_ok = Mock(spec=requests.Response, status_code=204)
        with _patch_get_pac(PACFile(proxy_pac_js)), \
             _patch_request_base(mock_ok) as request:
            for proxies_arg in ({}, proxy_parameter_for_requests('http://manual:80')):
                sess.get(arbitrary_url, proxies=proxies_arg)
                request.assert_called_with('GET', arbitrary_url, proxies=proxies_arg, allow_redirects=ANY)

    def test_pac_disabled(self):
        sess = PACSession(pac_enabled=False)
        mock_ok = Mock(spec=requests.Response, status_code=204)
        with _patch_get_pac(PACFile(proxy_pac_js)) as gp, \
                _patch_request_base(mock_ok) as request:
            assert sess.get(arbitrary_url).status_code == 204
            gp.assert_not_called()
            request.assert_called_with('GET', arbitrary_url, proxies=None, allow_redirects=ANY)
            # When re-enabled, PAC discovery should proceed and be honoured.
            sess.pac_enabled = True
            assert sess.get(arbitrary_url).status_code == 204
            gp.assert_called_with()
            request.assert_called_with('GET', arbitrary_url, proxies=fake_proxies_requests_arg, allow_redirects=ANY)

    @pytest.mark.parametrize('proxy_host', ['unreachable.local', 'localhost'])
    def test_bad_proxy_no_failover(self, proxy_host):
        """Verify that Requests returns ProxyError when given a non-existent proxy."""
        sess = PACSession(pac=PACFile(proxy_pac_js_tpl % 'PROXY %s:80' % proxy_host))
        with pytest.raises(ProxyError):
            sess.get(arbitrary_url)

    def test_pac_failover(self):
        """First proxy raises error. Transparently fail over to second proxy."""
        sess = PACSession(pac=PACFile(proxy_pac_js_tpl % 'PROXY a:80; PROXY b:80; DIRECT'))

        def fake_request(method, url, proxies=None, **kwargs):
            if proxies and proxies['http'] == 'http://a:80':
                raise ProxyError()

        with _patch_request_base(side_effect=fake_request) as request:
            sess.get(arbitrary_url)
            request.assert_has_calls([
                get_call(arbitrary_url, 'http://a:80'),
                get_call(arbitrary_url, 'http://b:80'),
            ])

    def test_pac_failover_to_direct(self):
        """Proxy fails. Next in line is DIRECT keyword."""
        sess = PACSession(pac=PACFile(proxy_pac_js))

        def fake_request_reject_proxy(method, url, proxies=None, **kwargs):
            if proxies and proxies['http'] is not None:
                raise ProxyError()

        with _patch_request_base(side_effect=fake_request_reject_proxy) as request:
            sess.get(arbitrary_url)
            request.assert_has_calls([
                get_call(arbitrary_url, fake_proxy_url),
                get_call(arbitrary_url, 'DIRECT'),
            ])

    def test_pac_failover_to_direct_also_fails(self):
        """Proxy fails. Next in line is DIRECT keyword, but direct connection also fails. Error should bubble up.
        Subsequent requests go straight to DIRECT, despite DIRECT failing."""
        sess = PACSession(pac=PACFile(proxy_pac_js))
        with _patch_request_base(side_effect=ProxyError()) as request:
            for _ in range(2):
                with pytest.raises(ProxyError):
                    sess.get(arbitrary_url)
        request.assert_has_calls([
            get_call(arbitrary_url, fake_proxy_url),
            get_call(arbitrary_url, 'DIRECT'),
            get_call(arbitrary_url, 'DIRECT'),
        ])

    def test_pac_no_failover_available_exc_case(self):
        """Special case where proxy fails but there's no DIRECT fallback. Error should bubble up,
        and all applicable proxies should be tried again in the next request. Proxy failure from exception."""
        sess = PACSession(pac=PACFile(proxy_pac_js_tpl % 'PROXY a:80; PROXY b:80'))
        for _ in range(2):
            with _patch_request_base(side_effect=ProxyError()) as request, \
                    pytest.raises(ProxyError):
                sess.get(arbitrary_url)
            request.assert_has_calls([
                get_call(arbitrary_url, 'http://a:80'),
                get_call(arbitrary_url, 'http://b:80'),
            ])

    def test_failover_using_custom_response_filter(self):
        """Use a custom response filter to say that HTTP 407 responses are considered a proxy failure,
        in order to trigger proxy failover."""

        def custom_response_filter(response): return response.status_code == 407

        proxy_fail_resp = Mock(spec=requests.Response, status_code=407)
        sess = PACSession(pac=PACFile(proxy_pac_js_tpl % 'PROXY a:80; PROXY b:80'),
                          response_proxy_fail_filter=custom_response_filter)
        with _patch_request_base(proxy_fail_resp) as request:
            # Both proxies failed due to 407 response, so return value is the same 407.
            assert sess.get(arbitrary_url).status_code == 407
            request.assert_has_calls([
                get_call(arbitrary_url, 'http://a:80'),
                get_call(arbitrary_url, 'http://b:80'),
            ])

    def test_failover_using_custom_exception_criteria(self):
        """Use a custom request exception filter to say that some arbitrary exception is considered a proxy failure,
        in order to trigger proxy failover."""

        def custom_exc_filter(exc): return isinstance(exc, NotImplementedError)

        def fake_request(method, url, proxies=None, **kwargs):
            if proxies and proxies['http'] == 'http://a:80':
                raise NotImplementedError()

        sess = PACSession(pac=PACFile(proxy_pac_js_tpl % 'PROXY a:80; PROXY b:80'),
                          exception_proxy_fail_filter=custom_exc_filter)

        with _patch_request_base(side_effect=fake_request) as request:
            sess.get(arbitrary_url)
            request.assert_has_calls([
                get_call(arbitrary_url, 'http://a:80'),
                get_call(arbitrary_url, 'http://b:80'),
            ])

    def test_post_init_proxy_auth(self):
        """Set proxy auth info after constructing PACSession, and ensure that PAC proxy URLs then reflect it."""
        sess = PACSession(pac=PACFile(proxy_pac_js_tpl % 'PROXY a:80;'))
        with _patch_request_base() as request:
            sess.get(arbitrary_url)  # Prime proxy resolver state.
            request.assert_has_calls([
                get_call(arbitrary_url, 'http://a:80'),
            ])

        sess.proxy_auth = HTTPProxyAuth('user', 'pwd')
        with _patch_request_base() as request:
            sess.get(arbitrary_url)
            request.assert_has_calls([
                get_call(arbitrary_url, 'http://user:pwd@a:80'),
            ])


class TestContextManager(object):
    def test_no_pac_no_env(self, monkeypatch):
        monkeypatch.delenv('HTTP_PROXY', raising=False)
        monkeypatch.delenv('HTTPS_PROXY', raising=False)
        with pac_context_for_url(arbitrary_url):
            assert not os.environ.get('HTTP_PROXY')
        assert not os.environ.get('HTTP_PROXY')

    def test_no_pac(self, monkeypatch):
        monkeypatch.setenv('HTTP_PROXY', 'http://env')
        with pac_context_for_url(arbitrary_url):
            assert os.environ['HTTP_PROXY'] == 'http://env'
        assert os.environ['HTTP_PROXY'] == 'http://env'

    def test_pac(self, monkeypatch):
        monkeypatch.setenv('HTTP_PROXY', 'http://env')
        with _patch_get_pac(PACFile(proxy_pac_js)):
            with pac_context_for_url(arbitrary_url):
                assert os.environ['HTTP_PROXY'] == fake_proxy_url
                assert os.environ['HTTPS_PROXY'] == fake_proxy_url
        assert os.environ['HTTP_PROXY'] == 'http://env'
