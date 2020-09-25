この proxyUtil は、PyPAC をフォークし、機能を追加した者です。
＜追加機能＞
virtualProxyEnviron()
    このオブジェクトは、PACから取得したプロキシ設定値を環境変数に適用するためのものです。
    def __init__(self, proxy_auth, url):
        ＜パラメータ＞
        proxy_auth = None
            プロキシ認証。デフォルトは認証なし
        URL = https://www.riken.jp/
            このURLと通信するためのPACを自動で取得します。デフォルトは理化学研究所
    def set_environ(self):
        環境変数をセットします。
    def unset_environ(self):
        環境変数の設定を元に戻します。

以下、およびその他のドキュメントについては、pypac、あるいはPyPAC表記をproxyUtilに読み替えてください。
フォーク元のPyPACへの影響が最小限となるように勤めています。
    


PyPAC: Proxy auto-config for Python
===================================

.. image:: https://img.shields.io/pypi/v/pypac.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/pypac
.. image:: https://readthedocs.org/projects/pypac/badge/?version=latest
    :target: https://pypac.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/travis/carsonyl/pypac.svg?maxAge=2592000
    :target: https://travis-ci.org/carsonyl/pypac
.. image:: https://ci.appveyor.com/api/projects/status/y7nxvu2feu87i39t/branch/master?svg=true
    :target: https://ci.appveyor.com/project/rbcarson/pypac/branch/master
.. image:: https://img.shields.io/coveralls/carsonyl/pypac/HEAD.svg?maxAge=2592000
    :target: https://coveralls.io/github/carsonyl/pypac
.. image:: https://img.shields.io/codacy/grade/71ac103b491d44efb94976ca5ea5d89c.svg?maxAge=2592000
    :target: https://www.codacy.com/app/carsonyl/pypac

PyPAC is a Python library for finding `proxy auto-config (PAC)`_ files and making HTTP requests
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
On macOS, PyPAC can obtain the PAC file URL from System Preferences.

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

PyPAC supports Python 2.7 and 3.4+.


Installation
------------

Install PyPAC using `pip <https://pip.pypa.io>`_::

    $ pip install pypac


Documentation
-------------

PyPAC's documentation is available at http://pypac.readthedocs.io/.
