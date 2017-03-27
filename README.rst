PyPAC: Proxy auto-config for Python
===================================

.. image:: https://img.shields.io/pypi/v/pypac.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/pypac
.. image:: https://img.shields.io/travis/rbcarson/pypac.svg?maxAge=2592000
    :target: https://travis-ci.org/rbcarson/pypac
.. image:: https://ci.appveyor.com/api/projects/status/y7nxvu2feu87i39t/branch/master?svg=true
    :target: https://ci.appveyor.com/project/rbcarson/pypac/branch/master
.. image:: https://img.shields.io/coveralls/rbcarson/pypac/HEAD.svg?maxAge=2592000
    :target: https://coveralls.io/github/rbcarson/pypac
.. image:: https://img.shields.io/codacy/grade/71ac103b491d44efb94976ca5ea5d89c.svg?maxAge=2592000
    :target: https://www.codacy.com/app/carsonyl/pypac

PyPAC is a pure-Python library for finding `proxy auto-config (PAC)`_ files and making HTTP requests
that respect them. PAC files are often used in organizations that need fine-grained and centralized control
of proxy settings. PyPAC supports Python 2.7 and 3.3+.

.. _proxy auto-config (PAC): https://en.wikipedia.org/wiki/Proxy_auto-config

PyPAC provides a subclass of a `Requests <http://docs.python-requests.org/en/master/>`_ ``Session``,
so you can start using it immediately, with any PAC file transparently discovered and honoured:

.. code-block:: python

    >>> from pypac import PACSession
    >>> session = PACSession()
    >>> session.get('http://example.org')
    ...

If a PAC file isn't found, then ``PACSession`` acts exactly like a regular ``Session``.

PyPAC can find PAC files according to the DNS portion of the `Web Proxy Auto-Discovery (WPAD)`_ protocol.
On Windows, PyPAC can also obtain the PAC file URL from the Internet Options dialog, via the registry.

If you know the URL for the PAC file to use, you can skip auto-discovery like so:

.. code-block:: python

    >>> from pypac import PACSession, get_pac
    >>> session = PACSession(pac=get_pac(url='http://example.corp.local/proxies.pac'))
    >>> session.get('http://example.org')
    ...

If there's no valid PAC at the given URL, ``get_pac()`` returns ``None``, and ``PACSession``
falls back to auto-discovery behaviour. By default, ``get_pac()`` accepts PAC files served with
a content type of ``application/x-ns-proxy-autoconfig`` or ``application/x-javascript-config``.
These are defined in the Netscape PAC specification.

.. _Web Proxy Auto-Discovery (WPAD): https://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol


Proxy authentication
--------------------

Basic proxy authentication can be specified in the PACSession constructor:

.. code-block:: python

    >>> from pypac import PACSession
    >>> from requests.auth import HTTPProxyAuth
    >>> session = PACSession(proxy_auth=HTTPProxyAuth('user', 'password'))
    >>> session.get('http://example.org')
    ...

To use NTLM authentication with proxies, install `requests-ntlm <https://github.com/requests/requests-ntlm>`_
and set ``PACSession.auth`` to an ``HttpNtlmAuth`` instance.


Security
--------

PAC files are JavaScript. PyPAC uses `Js2Py <https://github.com/PiotrDabkowski/Js2Py>`_
to parse and execute JavaScript. Js2Py was not designed for handling untrusted JavaScript,
and so it is unclear whether the handling of PAC files is sufficiently sandboxed to prevent
untrusted Python code execution.

When looking for a PAC file using DNS WPAD, the local machine's fully-qualified hostname is
checked against the `Mozilla Public Suffix List`_ to prevent requesting any PAC files outside
the scope of the organization. If the hostname's TLD isn't in the Public Suffix List, then
everything up to the final node is used in the search path. For example, a hostname of
foo.bar.local will result in a search for a PAC file from wpad.bar.local and wpad.local.

PyPAC uses the `tld <https://pypi.python.org/pypi/tld>`_ library to match TLDs.

.. _Mozilla Public Suffix List: https://publicsuffix.org/


What's missing
--------------

The DHCP portion of the Web Proxy Auto-Discovery (WPAD) protocol is not implemented.

PyPAC currently works with Requests by including a subclass of ``Session``.
No ready-to-use solutions are included for other HTTP libraries,
though PyPAC has all the building blocks needed to make one easily.

Pull requests to add these features are welcome.
