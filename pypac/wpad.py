"""
Tools for the Web Proxy Auto-Discovery Protocol.
"""
import logging
import socket

import tldextract

logger = logging.getLogger(__name__)

# First use of tldextract goes online to update its Public Suffix List cache. Stop it.
try:
    no_fetch_extract = tldextract.TLDExtract(cache_dir=None, suffix_list_urls=None)
except TypeError:
    # tldextract added cache_dir in v3.0.0, which also dropped PY27 support.
    # Maintain PY27 support / allow old tldextract by retrying here.
    no_fetch_extract = tldextract.TLDExtract(suffix_list_urls=None)


def proxy_urls_from_dns(local_hostname=None):
    """
    Generate URLs from which to look for a PAC file, based on a hostname.
    Fully-qualified hostnames are checked against the Public Suffix List to ensure that
    generated URLs don't go outside the scope of the organization.
    If the fully-qualified hostname doesn't have a recognized TLD,
    such as in the case of intranets with '.local' or '.internal',
    the TLD is assumed to be the part following the rightmost dot.

    :param str local_hostname: Hostname to use for generating the WPAD URLs.
        If not provided, the local hostname is used.
    :return: PAC URLs to try in order, according to the WPAD protocol.
        If the hostname isn't qualified or is otherwise invalid, an empty list is returned.
    :rtype: list[str]
    """
    if not local_hostname:
        local_hostname = socket.getfqdn()
    if (
        "." not in local_hostname
        or len(local_hostname) < 3
        or local_hostname.startswith(".")
        or local_hostname.endswith(".")
    ):
        return []

    parsed = no_fetch_extract(local_hostname)
    return wpad_search_urls(parsed.subdomain, parsed.registered_domain or parsed.domain)


def wpad_search_urls(subdomain_or_host, fld):
    """
    Generate URLs from which to look for a PAC file, based on the subdomain and TLD parts of
    a fully-qualified host name.

    :param str subdomain_or_host: Subdomain portion of the fully-qualified host name.
        For foo.bar.example.com, this is foo.bar.
    :param str fld: FLD portion of the fully-qualified host name.
        For foo.bar.example.com, this is example.com.
    :return: PAC URLs to try in order, according to the WPAD protocol.
    :rtype: list[str]
    """
    parts = subdomain_or_host.split(".")
    search_urls = []
    for i in range(1, len(parts) + 1):
        # Chop off host and move up the subdomain hierarchy.
        url = "http://wpad.{}/wpad.dat".format(".".join(parts[i:] + [fld]))
        search_urls.append(url)

    return search_urls
