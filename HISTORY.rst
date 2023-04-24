0.16.4 (2023-04-24)
-------------------

- Release using `Trusted Publishing <https://blog.pypi.org/posts/2023-04-20-introducing-trusted-publishers/>`_.

0.16.3 (2023-03-31)
-------------------

- ``isInNet()``: Return False immediately for invalid host arg. (#71)

0.16.2 (2023-03-26)
-------------------

- Handle boolean args to ``isInNet()``. (#69)
- Remove Python 3.5, 3.6 from CIB test matrix.
- Windows Python 2.7 CIB: Pin to dukpy 0.2.3.


0.16.1 (2022-11-08)
-------------------

- Disable ``tldextract`` caching. (#64) Thanks @mpkuth.


0.16.0 (2022-01-01)
-------------------

- Change ``tld`` dependency to ``tldextract``. (#61)


0.15.0 (2021-02-27)
-------------------

- Drop support for Python 3.4. (#48)
- Support more proxy keywords: HTTP, HTTPS, SOCKS4, SOCKS5. (#41)
- Absorb any exception from ``tld.get_tld()``, not just TldDomainNotFound. (#30) Thanks @santiavenda2.
- Reimplement ``dnsDomainIs(host, domain)`` as case-insensitive 'host ends with domain'. (#42, #57)


0.14.0 (2020-12-05)
-------------------

- Add ability to supply ``PACFile`` to ``pac_context_for_url()``. (#52) Thanks @alexrohvarger.


0.13.0 (2019-09-16)
-------------------

- Make it possible to configure the request for the PAC file. (#44) Thanks @SeyfSV.
- urlencode proxy username and password. (#46) Thanks @aslafy-z.


0.12.0 (2018-09-11)
-------------------

- Fix possible error when ``dnsResolve()`` fails. (#34) Thanks @maximinus.


0.11.0 (2018-09-08)
-------------------

- Require dukpy 0.2.2, to fix memory leak. (#32) Thanks @maximinus.
- Change Mac environment marker. (#30)
- Support Python 3.7.


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
