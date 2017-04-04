User guide
==========

Learn how to get started with PyPAC.
This guide assumes familiarity with the `Requests`_ library and its API.

.. _Requests: http://docs.python-requests.org/en/master/


Basic usage
-----------

The quickest way to get started is to use a :class:`PACSession <pypac.PACSession>`:

   >>> from pypac import PACSession
   >>> session = PACSession()
   >>> session.get('http://example.org')
   <Response [200]>

Behind the scenes, the first request made with the session will trigger the PAC auto-discovery process.
This process first looks for a PAC URL setting in Windows, and if not found,
moves on to the :ref:`DNS WPAD protocol <wpad>`.

Once a PAC file is found, it will be automatically consulted for every request.
If a PAC wasn't found, then :class:`PACSession` acts just like a :ref:`requests.Session <requests:session-objects>`.


Specify URL to your PAC
-----------------------

The :func:`get_pac() <pypac.get_pac>` function encapsulates the PAC file discovery process and returns
a :class:`PACFile <pypac.parser.PACFile>` object upon success. Instead of auto-discovery, this function
can be used to get and parse a PAC file from a given URL, which can then be passed to :class:`PACSession`::

   from pypac import PACSession, get_pac
   pac = get_pac(url='http://foo.corp.local/proxy.pac')
   session = PACSession(pac)

This is useful if you already know the URL for the PAC file to use, and want to skip auto-discovery.

Note that by default, PyPAC requires that PAC files be served with a content-type of either
``application/x-ns-proxy-autoconfig`` or ``application/x-javascript-config``.
Files served with other types are excluded from consideration as a PAC file.
This behaviour can be customized using the ``allowed_content_types`` keyword::

   pac = get_pac(url='http://foo.corp.local/proxy.txt',
                 allowed_content_types=['text/plain'])


Load PAC from a string or file
------------------------------

This is an unusual scenario, but also supported. Just instantiate your own :class:`PACFile <pypac.parser.PACFile>`,
passing it a string containing the PAC JavaScript. For instance, to load a local PAC file and use it with a
:class:`PACSession`::

   from pypac import PACSession
   from pypac.parser import PACFile

   with open('proxy.pac') as f:
      pac = PACFile(f.read())

   session = PACSession(pac)


Proxy authentication
--------------------

Proxy servers specified by a PAC file typically allow anonymous access.
However, PyPAC supports including Basic proxy authentication credentials::

   from pypac import PACSession
   from requests.auth import HTTPProxyAuth
   session = PACSession(proxy_auth=HTTPProxyAuth('user', 'pwd'))
   # or alternatively...
   session.proxy_auth = HTTPProxyAuth('user', 'pwd')

NTLM authentication for proxies may also be supported. Refer to the `requests-ntlm`_ project.

.. _requests-ntlm: https://github.com/requests/requests-ntlm


Custom proxy failover criteria
------------------------------

You can decide when a proxy from the PAC file should be considered unusable.
When a proxy is considered unusable, it's blacklisted, and the next proxy specified by the PAC file is used.
:class:`PACSession` can be configured with callables that define the criteria for failover.

One way to decide when to fail over is by inspecting the response to a request.
By default, PyPAC does not do this, but you may find it useful in case a failing proxy interjects with an
unusual response. Another use case is to skip proxies upon an HTTP 407 response::

   from pypac import PACSession
   import requests

   def failover_criteria(response):
       return response.status_code == requests.codes.proxy_authentication_required

   session = PACSession(response_proxy_fail_filter=failover_criteria)

Another way to decide proxy failover is based on any exception raised while making the request.
This can be configured by passing a callable for the ``exception_proxy_fail_filter`` keyword in the :class:`PACSession`
constructor. This callable takes an exception object as an argument, and returns true if failover should occur.
The default behaviour is to trigger proxy failover upon encountering
:class:`requests.exceptions.ConnectTimeout` or :class:`requests.exceptions.ProxyError`.

If all proxies specified by the PAC file have been blacklisted, and the PAC didn't return a final instruction
to go ``DIRECT``, then :class:`ProxyConfigExhaustedError <pypac.resolver.ProxyConfigExhaustedError>` is raised.


Errors and exceptions
---------------------

PyPAC defines some exceptions that can occur in the course of PAC auto-discovery, parsing, and execution.

:class:`MalformedPacError <pypac.parser.MalformedPacError>`
   PyPAC failed to parse a file that claims to be a PAC.

:class:`PyimportError <pypac.parser.PyimportError>`
   A PAC file contains the ``pyimport`` keyword specific to Js2Py.
   This represents a serious security issue.

:class:`PacComplexityError <pypac.parser.PacComplexityError>`
   PAC file is large enough that it couldn't be parsed under the current recursion limit.
   The recursion limit can be raised using :ref:`sys.setrecursionlimit`.

:class:`ProxyConfigExhaustedError <pypac.resolver.ProxyConfigExhaustedError>`
   All proxy servers for the given URL have been marked as failed,
   and the PAC file did not specify a final instruction to go ``DIRECT``.


Security considerations
-----------------------

Supporting and using PAC files comes with some security implications that are worth considering.


PAC discovery and parsing
^^^^^^^^^^^^^^^^^^^^^^^^^

PAC files are JavaScript. PyPAC uses `Js2Py <https://github.com/PiotrDabkowski/Js2Py>`_
to parse and execute JavaScript. Js2Py was not designed for handling untrusted JavaScript,
and so it is unclear whether the handling of PAC files is sufficiently sandboxed to prevent
untrusted Python code execution.

When looking for a PAC file using DNS WPAD, the local machine's fully-qualified hostname is
checked against the `Mozilla Public Suffix List`_ to prevent requesting any PAC files outside
the scope of the organization. If the hostname's TLD isn't in the Public Suffix List, then
everything up to the final node is used in the search path. For example, a hostname of
``foo.bar.local`` will result in a search for a PAC file from ``wpad.bar.local`` and ``wpad.local``.

PyPAC uses the `tld <https://pypi.python.org/pypi/tld>`_ library to match TLDs.

.. _Mozilla Public Suffix List: https://publicsuffix.org/


HTTPS-decrypting proxies
^^^^^^^^^^^^^^^^^^^^^^^^

Proxies operated by a firewall or web security gateway may may be configured with a
man-in-the-middle (MITM) certificate to allow decrypting HTTPS traffic for inspection.
Your organization may then provision its client machines with this certificate trusted.
Browsers such as Internet Explorer and Chrome, which honour the operating system's certificate store,
will accept the proxy's certificate.
However, Requests defaults to its own bundled CA certificates,
and thus SSL certificate verification will fail when using such a proxy.

A quick solution is to make your requests with the ``verify=False`` option.
Understand that this is an overly broad solution: while it allows your request to proceed and be
decrypted for inspection by your network proxy (an entity that you ostensibly trust),
it also disables SSL certificate verification entirely.
This means you request may be vulnerable to MITM attacks further down the line.


What's missing
--------------

The DHCP portion of the Web Proxy Auto-Discovery (WPAD) protocol is not implemented.

PyPAC currently works with Requests by including a subclass of :ref:`requests.Session <requests:session-objects>`.
No ready-to-use solutions are included for other HTTP libraries,
though PyPAC has all the building blocks needed to make one easily.

Pull requests to add these features are welcome.
