PyPAC: Proxy auto-config for Python
===================================

Release v\ |version|.

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

PyPAC is a pure-Python library for finding :doc:`proxy auto-config (PAC) <about_pac>` files and making HTTP requests
that respect them. PAC files are often used in organizations that need fine-grained and centralized control
of proxy settings.

.. _proxy auto-config (PAC): about_pac

PyPAC provides :class:`PACSession <pypac.PACSession>`,
a drop-in subclass of :ref:`requests.Session <requests:session-objects>`,
so you can start transparently finding and obeying PAC files immediately.


Features
--------

* The same Requests API that you already know and love
* Honour PAC setting from Windows Internet Options
* Follow DNS Web Proxy Auto-Discovery protocol
* Proxy failover and load balancing

PyPAC supports Python 2.7 and 3.3+.


Installation
------------

Install PyPAC using `pip <https://pip.pypa.io>`_::

    $ pip install pypac

The source is also `available on GitHub <https://github.com/rbcarson/pypac>`_.


Documentation
-------------
.. toctree::
   :maxdepth: 2

   about_pac
   user_guide
   api

.. toctree::
   :maxdepth: 1
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
