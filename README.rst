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
of proxy settings.

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

.. _Web Proxy Auto-Discovery (WPAD): https://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol


Features
--------

* The same Requests API that you already know and love
* Honour PAC setting from Windows Internet Options
* Follow DNS Web Proxy Auto-Discovery protocol
* Proxy authentication pass-through
* Proxy failover and load balancing

PyPAC supports Python 2.7 and 3.3+.


Installation
------------

Install PyPAC using `pip <https://pip.pypa.io>`_::

    $ pip install pypac


Documentation
-------------

PyPAC's documentation is available at http://pypac.readthedocs.io/.
