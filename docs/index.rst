PyPAC: Proxy auto-config for Python
===================================

Release v\ |version|.

.. image:: https://img.shields.io/pypi/v/pypac.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/pypac
.. image:: https://img.shields.io/travis/carsonyl/pypac.svg?maxAge=2592000
    :target: https://travis-ci.org/carsonyl/pypac
.. image:: https://ci.appveyor.com/api/projects/status/y7nxvu2feu87i39t/branch/master?svg=true
    :target: https://ci.appveyor.com/project/carsonyl/pypac/branch/master
.. image:: https://img.shields.io/coveralls/carsonyl/pypac/HEAD.svg?maxAge=2592000
    :target: https://coveralls.io/github/carsonyl/pypac
.. image:: https://img.shields.io/codacy/grade/71ac103b491d44efb94976ca5ea5d89c.svg?maxAge=2592000
    :target: https://www.codacy.com/app/carsonyl/pypac

PyPAC is a pure-Python library for finding :doc:`proxy auto-config (PAC) <about_pac>` files and making HTTP requests
that respect them. PAC files are often used in organizations that need fine-grained and centralized control
of proxy settings. :ref:`Are you using one? <who-uses-pacs>`

.. _proxy auto-config (PAC): about_pac

PyPAC provides :class:`PACSession <pypac.PACSession>`,
a drop-in subclass of :ref:`requests.Session <requests:session-objects>`,
so you can start transparently finding and obeying PAC files immediately.


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

The source is also `available on GitHub <https://github.com/carsonyl/pypac>`_.


Quickstart
----------

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

If you're looking to add *basic* PAC functionality to a library that you're using,
try the :func:`pac_context_for_url <pypac.pac_context_for_url>` context manager:

.. code-block:: python

   from pypac import pac_context_for_url
   import boto3

   with pac_context_for_url('https://example.amazonaws.com'):
       client = boto3.client('sqs')
       client.list_queues()

This sets up proxy environment variables at the start of the scope, based on any auto-discovered PAC and the given URL.
:func:`pac_context_for_url <pypac.pac_context_for_url>` should work for any library
that honours proxy environment variables.


Documentation
-------------
.. toctree::
   :maxdepth: 2

   about_pac
   user_guide
   api

.. toctree::
   :maxdepth: 1

   licence
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
