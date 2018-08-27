0.10.1 (2018-08-26)
-------------------

- Require tld 0.9.x. (#29)


0.10.0 (2018-08-26)
-------------------

- Switch JavaScript interpreter to dukpy. (#24)
- Fix ``pac_context_for_url()`` erroring with ``DIRECT`` PAC setting. (#27)
- Fix warning about invalid escape sequence (#26). Thanks @BoboTiG.


0.9.0 (2018-06-02)
------------------

- Add macOS support for PAC in System Preferences (#23). Thanks @LKleinNux.
- The `from_registry` argument on `pypac.get_pac()` and `pypac.collect_pac_urls()`
  is now deprecated and will be removed in 1.0.0. Use `from_os_settings` instead.


0.8.1 (2018-03-01)
------------------

- Defer Js2Py import until it's needed. It uses a lot of memory.
  See #20 for details.


0.8.0 (2018-02-28)
------------------

- Add support for ``file://`` PAC URLs on Windows.


0.7.0 (2018-02-21)
------------------

- Drop support for Python 3.3.
- Add doc explaining how to use ``pac_context_for_url()``.
- Internal changes to dev and test processes.


0.6.0 (2018-01-28)
------------------

- Add ``pac_context_for_url()``, a context manager that adds basic PAC functionality
  through proxy environment variables.


0.5.0 (2018-01-18)
------------------

- Accept PAC files served with no ``Content-Type`` header.


0.4.0 (2017-11-07)
------------------

- Add ``recursion_limit`` keyword argument to ``PACSession`` and ``PACFile``.
  The default is an arbitrarily high value (10000), which should cover most applications.
- Exclude port numbers from ``host`` passed to ``FindProxyForURL(url, host)``.


0.3.1 (2017-06-23)
------------------

- Update GitHub username.


0.3.0 (2017-04-12)
------------------
- Windows: Get system auto-proxy config setting using ``winreg`` module.
- Windows: Accept local filesystem paths from system proxy auto-config setting.
- Raise ``PacComplexityError`` when recursion limit is hit while parsing PAC file.
- Support setting ``PACSession.proxy_auth`` and ``ProxyResolver.proxy_auth`` after constructing an instance.
- Narrative docs.


0.2.1 (2017-01-19)
------------------

- Require Js2Py >= 0.43 for Python 3.6 support, and to avoid needing to monkeypatch out ``pyimport``.


0.1.0 (2016-06-12)
------------------

- First release.
