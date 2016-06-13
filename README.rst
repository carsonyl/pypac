PyPAC: Proxy auto-config file discovery and parsing
===================================================

PyPAC is a pure-Python library for finding, downloading, and parsing
`proxy auto-config (PAC) <https://en.wikipedia.org/wiki/Proxy_auto-config>`_ files.
PAC files are often used in organizations that need fine-grained control of proxy settings.
PyPAC supports Python 2.7 and 3.3+.

PyPAC provides a subclass of a `Requests <http://docs.python-requests.org/en/master/>`_ ``Session``,
so you can start using it immediately, with the PAC file transparently discovered and honoured:

.. code-block:: python

    >>> from pypac import PACSession
    >>> session = PACSession()
    >>> session.get('http://example.org')
    ...

PyPAC can find PAC files according to the DNS portion of the
`Web Proxy Auto-Discovery (WPAD) <https://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol>`_ protocol.
On Windows, PyPAC can obtain the PAC file URL from the registry.


Proxy authentication
--------------------

Basic proxy authentication can be specified via the PACSession constructor:

.. code-block:: python

    >>> from pypac import PACSession
    >>> from requests.auth import HTTPProxyAuth
    >>> session = PACSession(proxy_auth=HTTPProxyAuth('user', 'password'))
    >>> session.get('http://example.org')
    ...

To use NTLM authentication with proxies, install `requests-ntlm <https://github.com/requests/requests-ntlm>`_
and try setting ``PACSession.auth`` to an ``HttpNtlmAuth`` instance.


Security
--------

PAC files are JavaScript. PyPAC uses `Js2Py <https://github.com/PiotrDabkowski/Js2Py>`_
to parse and execute JavaScript. Js2Py was not designed for handling untrusted JavaScript,
and so it is unclear whether the handling of PAC files is sufficiently sandboxed to prevent
untrusted Python code execution.

When looking for a PAC file using DNS WPAD, the local machine's fully-qualified hostname is
checked against the Mozilla Public Suffix List to prevent requesting any PAC files outside
the scope of the organization. If the hostname's TLD isn't in the Public Suffix List, then
everything up to the final node is used in the search path. For example, a hostname of
foo.bar.local will result in a search for a PAC file from wpad.bar.local and wpad.local.


What's missing
--------------

The DHCP portion of the Web Proxy Auto-Discovery (WPAD) protocol is not implemented.

PyPAC currently works with Requests by including a subclass of Session.
No ready-to-use solutions are included for other HTTP libraries,
though PyPAC has all the building blocks needed to make one easily.

Pull requests to add these features are welcome.
