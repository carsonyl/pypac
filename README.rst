PyPAC: Proxy auto-config for Python
===================================

.. image:: https://img.shields.io/pypi/v/pypac.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/pypac
.. image:: https://img.shields.io/pypi/pyversions/pypac.svg
    :target: https://pypi.python.org/pypi/pypac
.. image:: https://readthedocs.org/projects/pypac/badge/?version=latest
    :target: https://pypac.readthedocs.io/en/latest/?badge=latest
.. image:: https://github.com/carsonyl/pypac/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/carsonyl/pypac/actions/workflows/tests.yml

PyPAC is a Python library for finding `proxy auto-config (PAC)`_ files and making HTTP requests
that respect them. PAC files are often used in organizations that need fine-grained and centralized control
of proxy settings.

PyPAC can find PAC files according to the DNS portion of the `Web Proxy Auto-Discovery (WPAD)`_ protocol.
On Windows, PyPAC will automatically get the PAC file URL from the Internet Options dialog.
On macOS, PyPAC will automatically get the PAC file URL from System Preferences.

.. _proxy auto-config (PAC): https://en.wikipedia.org/wiki/Proxy_auto-config

PyPAC provides a subclass of a `Requests <http://docs.python-requests.org/en/master/>`_ ``Session``,
so you can start using it immediately, with any PAC file transparently discovered and honoured:

.. code-block:: python

    >>> from pypac import PACSession
    >>> session = PACSession()
    >>> session.get('http://example.org')
    ...

If a PAC file isn't found, then ``PACSession`` behaves like a regular ``Session``.

.. _Web Proxy Auto-Discovery (WPAD): https://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol

If you're looking to add *basic* PAC functionality to a library that you're using,
try the ``pac_context_for_url()`` context manager:

.. code-block:: python

   from pypac import pac_context_for_url
   import boto3

   with pac_context_for_url('https://example.amazonaws.com'):
       client = boto3.client('sqs')
       client.list_queues()

This sets up proxy environment variables at the start of the scope, based on any auto-discovered PAC and the given URL.
``pac_context_for_url()`` should work for any library
that honours proxy environment variables.


Features
--------

* The same Requests API that you already know and love
* Honour PAC setting from Windows Internet Options and macOS System Preferences
* Follow DNS Web Proxy Auto-Discovery protocol
* Proxy authentication pass-through
* Proxy failover and load balancing
* Generic components for adding PAC support to other code

PyPAC supports Python 2.7 and 3.5+.


Installation
------------

Install PyPAC using `pip <https://pip.pypa.io>`_::

    $ python -m pip install pypac


Documentation
-------------

PyPAC's documentation is available at http://pypac.readthedocs.io/.
