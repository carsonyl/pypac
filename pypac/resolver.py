"""
Tools for working with a given PAC file and its return values.
"""
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from pypac.parser import parse_pac_value


class ProxyResolver(object):
    """
    Handles the lookup of the proxy to use for any given URL, including proxy failover logic.
    """

    def __init__(self, pac, proxy_auth=None, socks_scheme="socks5"):
        """
        :param pypac.parser.PACFile pac: Parsed PAC file.
        :param requests.auth.HTTPProxyAuth proxy_auth: Username and password proxy authentication.
            If provided, then all proxy URLs returned will include these credentials.
        :param str socks_scheme: Scheme to assume for SOCKS proxies. `socks5` by default.
        """
        self.pac = pac
        self._proxy_auth = proxy_auth
        self.socks_scheme = socks_scheme

        self._offline_proxies = set()
        self._cache = {}  # Cache parsed version of FindProxyForURL() return values.

    @property
    def proxy_auth(self):
        """Proxy authentication object."""
        return self._proxy_auth

    @proxy_auth.setter
    def proxy_auth(self, value):
        self._proxy_auth = value
        self._cache.clear()
        self.unban_all()

    def get_proxies(self, url):
        """
        Get the proxies that are applicable to a given URL, according to the PAC file.

        :param str url: The URL for which to find appropriate proxies.
        :return: All the proxies that apply to the given URL.
            Can be empty, which means to abort the request.
        :rtype: list[str]
        """
        hostname = urlparse(url).hostname
        if hostname is None:
            # URL has no hostname, and PAC functions don't expect to receive nulls.
            hostname = ""

        value_from_js_func = self.pac.find_proxy_for_url(url, hostname)
        if value_from_js_func in self._cache:
            return self._cache[value_from_js_func]

        config_values = parse_pac_value(value_from_js_func, self.socks_scheme)
        if self._proxy_auth:
            config_values = [add_proxy_auth(value, self._proxy_auth) for value in config_values]

        self._cache[value_from_js_func] = config_values

        return config_values

    def get_proxy(self, url):
        """
        Get a proxy to use for a given URL, excluding any banned ones.

        :param str url: The URL for which to find an appropriate proxy.
        :return: A proxy to use for the URL,
            or the string 'DIRECT', which means a proxy is not to be used.
            Can be ``None``, which means to not attempt the request.
        :rtype: str|None
        """
        proxies = self.get_proxies(url)
        for proxy in proxies:
            if proxy == "DIRECT" or proxy not in self._offline_proxies:
                return proxy

    def get_proxy_for_requests(self, url):
        """
        Get proxy configuration for a given URL, in a form ready to use with the Requests library.

        :param str url: The URL for which to obtain proxy configuration.
        :returns: Proxy configuration in a form recognized by Requests, for use with the ``proxies`` parameter.
        :rtype: dict
        :raises ProxyConfigExhaustedError: If no proxy is configured or available,
            and 'DIRECT' is not configured as a fallback.
        """
        proxy = self.get_proxy(url)
        if not proxy:
            raise ProxyConfigExhaustedError(url)
        return proxy_parameter_for_requests(proxy)

    def ban_proxy(self, proxy_url):
        """
        Ban a proxy such that :meth:`get_proxy` and :meth:`get_proxy_for_requests` will never return it.

        :param str proxy_url: URL for the proxy to ban.
            Must match a proxy URL returned by this class, including any authentication info.
        """
        self._offline_proxies.add(proxy_url)

    def unban_all(self):
        """Unban any banned proxies."""
        self._offline_proxies.clear()


def add_proxy_auth(possible_proxy_url, proxy_auth):
    """
    Add a username and password to a proxy URL, if the input value is a proxy URL.

    :param str possible_proxy_url: Proxy URL or ``DIRECT``.
    :param requests.auth.HTTPProxyAuth proxy_auth: Proxy authentication info.
    :returns: Proxy URL with auth info added, or ``DIRECT``.
    :rtype: str
    """
    if possible_proxy_url == "DIRECT":
        return possible_proxy_url
    parsed = urlparse(possible_proxy_url)
    return "{0}://{1}:{2}@{3}".format(
        parsed.scheme, quote_plus(proxy_auth.username), quote_plus(proxy_auth.password), parsed.netloc
    )


def proxy_parameter_for_requests(proxy_url_or_direct):
    """
    :param str proxy_url_or_direct: Proxy URL, or ``DIRECT``. Cannot be empty.
    :return: Value for use with the ``proxies`` parameter in Requests.
    :rtype: dict
    """
    if proxy_url_or_direct == "DIRECT":
        # This stops Requests from inheriting environment proxy settings.
        proxy_url_or_direct = None
    return {
        "http": proxy_url_or_direct,
        "https": proxy_url_or_direct,
    }


class ProxyConfigExhaustedError(Exception):
    def __init__(self, for_url):
        super(ProxyConfigExhaustedError, self).__init__("No proxy configured or available for '{}'".format(for_url))
