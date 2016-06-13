import js2py
import warnings
from js2py.base import PyJsException

from pypac.parser_functions import function_injections


class PACFile(object):
    def __init__(self, pac_js):
        """
        :param str pac_js: JavaScript that defines the FindProxyForURL() function.
        :raises MalformedPacError: If the JavaScript could not be parsed, does not define FindProxyForURL(),
            or is otherwise invalid.
        :raises PyImportError: If the JavaScript tries to use Js2Py's `pyimport` keyword,
            which is not legitimate in the context of a PAC file.
        """
        # Disallow parsing of the unsafe 'pyimport' statement in Js2Py by monkey-patching the parser.
        # Try to be a good citizen by restoring original functionality once we're done.
        # Don't want to make Mock a dependency just for this.
        orig_pyimport_meth = js2py.translators.pyjsparser.PyJsParser.parsePyimportStatement
        js2py.translators.pyjsparser.PyJsParser.parsePyimportStatement = _raise_pyimport_error
        try:
            context = js2py.EvalJs(function_injections)
            context.execute(pac_js)
            # A test call to weed out errors like unimplemented functions.
            context.FindProxyForURL('/', '0.0.0.0')

            self._context = context
            self._func = context.FindProxyForURL
        except PyJsException:  # as e:
            raise MalformedPacError()  # from e
        finally:
            js2py.translators.pyjsparser.PyJsParser.parsePyimportStatement = orig_pyimport_meth

    def find_proxy_for_url(self, url, host):
        """
        Call FindProxyForURL() with the given arguments.

        :param str url: The full URL.
        :param str host: The URL's host.
        :return: Result of evaluating the FindProxyForURL() JavaScript function in the PAC file.
        :rtype: str
        """
        return self._func(url, host)


def _raise_pyimport_error(*args, **kwargs):
    raise PyimportError()


class MalformedPacError(Exception):
    def __init__(self, msg=None):
        if not msg:
            msg = "Malformed PAC file"
        super(MalformedPacError, self).__init__(msg)


class PyimportError(MalformedPacError):
    def __init__(self):
        super(PyimportError, self).__init__("PAC file contains pyimport statement. "
                                            "Ensure that the source of your PAC file is trustworthy")


def parse_pac_value(value, socks_scheme=None):
    """
    Parse the return value of FindProxyForURL() into a fairly usable list.
    List elements will either be the string 'DIRECT' or a proxy URL.

    For example, the result of parsing `PROXY example.local:8080; DIRECT`
    is a list of size 2, containing strings `http://example.local:8080` and `DIRECT`.

    :param str value: Any value returned by FindProxyForURL().
    :param str socks_scheme: Scheme to assume for SOCKS proxies. `socks5` by default.
    :returns: Parsed output, with invalid elements ignored. Warnings are logged for invalid elements.
    :rtype: list[str]
    """
    config = []
    for element in value.split(';'):
        element = element.strip()
        if not element:
            continue
        try:
            config.append(proxy_url(element, socks_scheme))
        except ValueError as e:
            warnings.warn(str(e))
    return config


def proxy_url(value, socks_scheme=None):
    """
    Parse a single proxy config value from FindProxyForURL() into a more usable element.

    :param str value: Value to parse, e.g.: `DIRECT`, `PROXY example.local:8080`, or `SOCKS example.local:8080`.
    :param str socks_scheme: Scheme to assume for SOCKS proxies. `socks5` by default.
    :returns: Parsed value, e.g.: `DIRECT`, `http://example.local:8080`, or `socks5://example.local:8080`.
    :rtype: str
    :raises ValueError: If input value is invalid.
    """
    if value.upper() == 'DIRECT':
        return 'DIRECT'
    parts = value.split()

    if len(parts) == 2:
        keyword, proxy = parts[0].upper(), parts[1]
        if keyword == 'PROXY':
            return 'http://' + proxy
        if keyword == 'SOCKS':
            if not socks_scheme:
                socks_scheme = 'socks5'
            return '{0}://{1}'.format(socks_scheme, proxy)

    raise ValueError("Unrecognized proxy config value '{}'".format(value))
