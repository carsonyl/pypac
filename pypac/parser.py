"""
Functions and classes for parsing and executing PAC files.
"""

import itertools
import warnings

import dukpy

from pypac.parser_functions import function_injections
from pypac.parser_functions_ex import function_injections as ipv6_functions


def _inject_function_into_js(context, name, func):
    """
    Inject a Python function into the global scope of a dukpy JavaScript interpreter context.

    :type context: dukpy.JSInterpreter
    :param name: Name to give the function in JavaScript.
    :param func: Python function.
    """
    context.export_function(name, func)
    context.evaljs(
        """;
        {name} = function() {{
            var args = Array.prototype.slice.call(arguments);
            args.unshift('{name}');
            return call_python.apply(null, args);
        }};
    """.format(name=name)
    )


class PACFile(object):
    """
    Represents a PAC file.

    JavaScript parsing and execution is handled by the `dukpy`_ library.

    .. _dukpy: https://github.com/amol-/dukpy
    """

    def __init__(self, pac_js, **kwargs):
        """
        Load a PAC file from a given string of JavaScript.
        Errors during parsing and validation may raise a specialized exception.

        :param str pac_js: JavaScript that defines the ``FindProxyForURL()``
            or ``FindProxyForURLEx()`` function.
        :raises MalformedPacError: If the JavaScript could not be parsed,
            does not define the expected function, or is otherwise invalid.
        """
        if kwargs.get("recursion_limit"):
            import warnings

            warnings.warn("recursion_limit is deprecated and has no effect. It will be removed in a future release.")

        try:
            self._context = dukpy.JSInterpreter()
            # IPv6 functions always available instead of only in FindProxyForURLEx(),
            # contrary to Microsoft spec.
            # https://issues.chromium.org/issues/40955802
            for name, func in itertools.chain(function_injections.items(), ipv6_functions.items()):
                _inject_function_into_js(self._context, name, func)
            self._context.evaljs(pac_js)

            # A test call to weed out errors like unimplemented functions.
            self.find_proxy_for_url("/", "0.0.0.0")

        except dukpy.JSRuntimeError as e:
            raise MalformedPacError(original_exc=e)  # from e
        self.js = pac_js

    def find_proxy_for_url(self, url, host):
        """
        Call ``FindProxyForURL()`` in the PAC file with the given arguments.
        If ``FindProxyForURL()`` is not defined, then call ``FindProxyForURLEx()`` instead.

        :param str url: The full URL.
        :param str host: The URL's host.
        :return: Result of evaluating the ``FindProxyForURL()`` or ``FindProxyForURLEx()``
            JavaScript function in the PAC file.
        :rtype: str
        """
        try:
            return self._context.evaljs("FindProxyForURL(dukpy['url'], dukpy['host'])", url=url, host=host)
        except dukpy.JSRuntimeError as e:
            if "ReferenceError: identifier 'FindProxyForURL' undefined" not in str(e):
                raise
            return self._context.evaljs("FindProxyForURLEx(dukpy['url'], dukpy['host'])", url=url, host=host)


class MalformedPacError(Exception):
    def __init__(self, msg=None, original_exc=None):
        if not msg:
            msg = "Malformed PAC file"
        self.original_exc = original_exc
        if original_exc:
            msg += " ({})".format(original_exc)
        super(MalformedPacError, self).__init__(msg)


class PyimportError(MalformedPacError):
    def __init__(self):
        super(PyimportError, self).__init__(
            "PAC file contains pyimport statement. Ensure that the source of your PAC file is trustworthy"
        )
        import warnings

        warnings.warn("PyimportError is deprecated and will be removed in a future release.")


class PacComplexityError(RuntimeError):
    def __init__(self):
        super(PacComplexityError, self).__init__(
            "Maximum recursion depth exceeded while parsing PAC file. Raise it using sys.setrecursionlimit()"
        )
        import warnings

        warnings.warn("PacComplexityError is deprecated and will be removed in a future release.")


def parse_pac_value(value, socks_scheme=None):
    """
    Parse the return value of ``FindProxyForURL()`` into a list.
    List elements will either be the string "DIRECT" or a proxy URL.

    For example, the result of parsing ``PROXY example.local:8080; DIRECT``
    is a list containing strings ``http://example.local:8080`` and ``DIRECT``.

    :param str value: Any value returned by ``FindProxyForURL()``.
    :param str socks_scheme: Scheme to assume for SOCKS proxies. ``socks5`` by default.
        Case-insensitive.
    :returns: Parsed output, with invalid elements ignored. Warnings are logged for invalid elements.
    :rtype: list[str]
    """
    config = []
    for element in value.split(";"):
        element = element.strip()
        if not element:
            continue
        try:
            config.append(proxy_url(element, socks_scheme))
        except ValueError as e:
            warnings.warn(str(e))
    return config


_PROXY_SCHEMES = {"HTTP", "HTTPS", "SOCKS4", "SOCKS5"}


def proxy_url(value, socks_scheme=None):
    """
    Parse a single proxy config value from FindProxyForURL() into a more usable element.

    The recognized keywords are ``DIRECT``, ``PROXY``, ``SOCKS``, ``SOCKS4``, and ``SOCKS5``.
    See https://developer.mozilla.org/en-US/docs/Web/HTTP/Proxy_servers_and_tunneling/Proxy_Auto-Configuration_PAC_file#return_value_format

    :param str value: Value to parse, e.g.: ``DIRECT``, ``PROXY example.local:8080``, or ``SOCKS example.local:8080``.
    :param str socks_scheme: Scheme to assume for SOCKS proxies. ``socks5`` by default.
        Case-insensitive.
    :returns: Parsed value, e.g.: ``DIRECT``, ``http://example.local:8080``, or ``socks5://example.local:8080``.
    :rtype: str
    :raises ValueError: If input value is invalid.
    """
    if value.upper() == "DIRECT":
        return "DIRECT"
    parts = value.split()

    if len(parts) == 2:
        keyword, proxy = parts[0].upper(), parts[1]
        if keyword == "PROXY":
            keyword = "HTTP"
        elif keyword == "SOCKS":
            socks_scheme = socks_scheme.upper() if socks_scheme else "SOCKS5"
            if socks_scheme not in _PROXY_SCHEMES:
                raise ValueError("socks_scheme '{}' is not one of {}".format(socks_scheme, ", ".join(_PROXY_SCHEMES)))
            keyword = socks_scheme

        if keyword in _PROXY_SCHEMES:
            return "{0}://{1}".format(keyword.lower(), proxy)

    raise ValueError("Unrecognized proxy config value '{}'".format(value))
