"""
Python implementations of JavaScript functions needed to execute a PAC file.

These are injected into the JavaScript execution context.
They aren't meant to be called directly from Python, so the function signatures may look unusual.

Most docstrings below are adapted from http://findproxyforurl.com/netscape-documentation/.
"""
import socket
import struct
from calendar import monthrange
from datetime import date, datetime, time
from fnmatch import fnmatch

from requests.utils import is_ipv4_address

try:
    basestring  # noqa
except NameError:
    basestring = str


def dnsDomainIs(host, domain):
    """
    :param str host: is the hostname from the URL.
    :param str domain: is the domain name to test the hostname against.
    :return: true iff the domain of hostname matches.
    :rtype: bool
    """
    return host.lower().endswith(domain.lower())


def shExpMatch(host, pattern):
    """
    Case-insensitive host comparison using a shell expression pattern.

    :param str host:
    :param str pattern: Shell expression pattern to match against.
    :rtype: bool
    """
    return fnmatch(host.lower(), pattern.lower())


def _address_in_network(ip, netaddr, mask):
    """
    Like :func:`requests.utils.address_in_network` but takes a quad-dotted netmask.
    """
    ipaddr = struct.unpack("=L", socket.inet_aton(ip))[0]
    netmask = struct.unpack("=L", socket.inet_aton(mask))[0]
    network = struct.unpack("=L", socket.inet_aton(netaddr))[0] & netmask
    return (ipaddr & netmask) == (network & netmask)


def isInNet(host, pattern, mask):
    """
    Pattern and mask specification is done the same way as for SOCKS configuration.

    :param str host: a DNS hostname, or IP address.
        If a hostname is passed, it will be resolved into an IP address by this function.
    :param str pattern: an IP address pattern in the dot-separated format
    :param str mask: mask for the IP address pattern informing which parts of
        the IP address should be matched against. 0 means ignore, 255 means match.
    :returns: True iff the IP address of the host matches the specified IP address pattern.
    :rtype: bool
    """
    if not isinstance(host, basestring) or not host:
        return False
    pattern = str(pattern)
    mask = str(mask)
    host_ip = host if is_ipv4_address(host) else dnsResolve(host)
    if not host_ip or not is_ipv4_address(pattern) or not is_ipv4_address(mask):
        return False
    return _address_in_network(host_ip, pattern, mask)


def localHostOrDomainIs(host, hostdom):
    """
    :param str host: the hostname from the URL.
    :param str hostdom: fully qualified hostname to match against.
    :return: true if the hostname matches exactly the specified hostname,
        or if there is no domain name part in the hostname, but the unqualified hostname matches.
    :rtype: bool
    """
    return hostdom.lower().startswith(host.lower())


def myIpAddress():
    """
    :returns: the IP address of the host that the Navigator is running on,
        as a string in the dot-separated integer format.
    :rtype: str
    """
    return dnsResolve(socket.gethostname())


def dnsResolve(host):
    """
    Resolves the given DNS hostname into an IP address, and returns it in the dot separated format as a string.
    Returns an empty string if there is an error

    :param str host: hostname to resolve
    :return: Resolved IP address, or empty string if resolution failed.
    :rtype: str
    """
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return ""


def isPlainHostName(host):
    """
    :param str host: the hostname from the URL (excluding port number).
    :return: True iff there is no domain name in the hostname (no dots).
    :rtype: bool
    """
    return dnsDomainLevels(host) == 0


def isResolvable(host):
    """
    Tries to resolve the hostname.

    :param str host: is the hostname from the URL.
    :return: true if succeeds.
    :rtype: bool
    """
    try:
        socket.gethostbyname(host)
    except socket.gaierror:
        return False
    return True


def dnsDomainLevels(host):
    """
    :param str host: is the hostname from the URL.
    :return: the number (integer) of DNS domain levels (number of dots) in the hostname.
    :rtype: int
    """
    return host.count(".")


def weekdayRange(start_day, end_day=None, gmt=None):
    """
    Accepted forms:

    * ``weekdayRange(wd1)``
    * ``weekdayRange(wd1, gmt)``
    * ``weekdayRange(wd1, wd2)``
    * ``weekdayRange(wd1, wd2, gmt)``

    If only one parameter is present, the function yields a true value on the weekday that the parameter represents.
    If the string "GMT" is specified as a second parameter, times are taken to be in GMT, otherwise in local timezone.

    If both ``wd1`` and wd2`` are defined, the condition is true if the current weekday is in between those two weekdays.
    Bounds are inclusive. If the ``gmt`` parameter is specified, times are taken to be in GMT,
    otherwise the local timezone is used.

    Weekday arguments are one of ``MON TUE WED THU FRI SAT SUN``.

    :param str start_day: Weekday string.
    :param str end_day: Weekday string.
    :param str gmt: is either the string: GMT or is left out.
    :rtype: bool
    """
    now_weekday_num = _now("GMT" if end_day == "GMT" else gmt).weekday()
    weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    if start_day not in weekdays or (end_day not in weekdays and end_day != "GMT"):
        return False

    start_day_num = weekdays.index(start_day)
    if start_day and (not end_day or end_day == "GMT"):
        return start_day_num == now_weekday_num

    end_day_num = weekdays.index(end_day)
    if end_day_num < start_day_num:  # Range past Sunday.
        return now_weekday_num >= start_day_num or now_weekday_num <= end_day_num

    return start_day_num <= now_weekday_num <= end_day_num


def _now(gmt=None):
    """
    :param str|None gmt: Use 'GMT' to get GMT.
    :rtype: datetime
    """
    return datetime.utcnow() if gmt == "GMT" else datetime.today()


def dateRange(*args):
    """
    Accepted forms:

    * ``dateRange(day)``
    * ``dateRange(day1, day2)``
    * ``dateRange(mon)``
    * ``dateRange(month1, month2)``
    * ``dateRange(year)``
    * ``dateRange(year1, year2)``
    * ``dateRange(day1, month1, day2, month2)``
    * ``dateRange(month1, year1, month2, year2)``
    * ``dateRange(day1, month1, year1, day2, month2, year2)``
    * ``dateRange(day1, month1, year1, day2, month2, year2, gmt)``

    ``day``
        is the day of month between 1 and 31 (as an integer).
    ``month``
        is one of the month strings:
            ``JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC``
    ``year``
        is the full year number, for example 1995 (but not 95). Integer.
    ``gmt``
        is either the string "GMT", which makes time comparison occur in GMT timezone;
        if left unspecified, times are taken to be in the local timezone.

    Even though the above examples don't show,
    the "GMT" parameter can be specified in any of the 9 different call profiles, always as the last parameter.

    If only a single value is specified (from each category: ``day``, ``month``, ``year``),
    the function returns a true value only on days that match that specification.
    If both values are specified, the result is true between those times, including bounds.

    :rtype: bool
    """
    months = [None, "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    gmt_arg_present = (len(args) == 2 and args[1] == "GMT") or (len(args) % 2 == 1 and len(args) > 1)
    if gmt_arg_present:
        # Remove and handle GMT argument.
        today = _now(args[-1])
        args = args[:-1]
    else:
        today = _now()
    today = today.date()

    num_args = len(args)
    try:
        if num_args == 1:
            # Match only against the day, month, or year.
            val = args[0]
            if val in months:
                return today.month == months.index(val)
            if 1 <= val <= 31:
                return today.day == val
            return today.year == val
        if num_args == 2:
            # Match against inclusive range of day, month, or year.
            a1, a2 = args
            if a1 in months and a2 in months:
                return months.index(a1) <= today.month <= months.index(a2)
            if 1 <= a1 <= 31:
                return a1 <= today.day <= a2
            return a1 <= today.year <= a2
        if num_args == 4:
            # Match against inclusive range of day-month or month-year.
            if args[0] in months and args[2] in months:
                m1, y1, m2, y2 = args
                m1, m2 = months.index(m1), months.index(m2)
                return date(y1, m1, 1) <= today <= date(y2, m2, monthrange(y2, m2)[1])
            if args[1] in months and args[3] in months:
                d1, m1, d2, m2 = args
                m1, m2 = months.index(m1), months.index(m2)
                return date(today.year, m1, d1) <= today <= date(today.year, m2, d2)
        if num_args == 6:
            # Match against inclusive range of start date and end date.
            d1, m1, y1, d2, m2, y2 = args
            m1, m2 = months.index(m1), months.index(m2)
            return date(y1, m1, d1) <= today <= date(y2, m2, d2)
    except (ValueError, TypeError):
        # Probably an invalid M/D/Y argument.
        return False

    return False


def timeRange(*args):
    """
    Accepted forms:

    * ``timeRange(hour)``
    * ``timeRange(hour1, hour2)``
    * ``timeRange(hour1, min1, hour2, min2)``
    * ``timeRange(hour1, min1, sec1, hour2, min2, sec2)``
    * ``timeRange(hour1, min1, sec1, hour2, min2, sec2, gmt)``

    ``hour``
        is the hour from 0 to 23. (0 is midnight, 23 is 11 pm.)
    ``min``
        minutes from 0 to 59.
    ``sec``
        seconds from 0 to 59.
    ``gmt``
        either the string "GMT" for GMT timezone, or not specified, for local timezone.
        Again, even though the above list doesn't show it, this parameter may be present in each of
        the different parameter profiles, always as the last parameter.

    :return: True during (or between) the specified time(s).
    :rtype: bool
    """
    gmt_arg_present = (len(args) == 2 and args[1] == "GMT") or (len(args) % 2 == 1 and len(args) > 1)
    if gmt_arg_present:
        # Remove and handle GMT argument.
        today = _now(args[-1])
        args = args[:-1]
    else:
        today = _now()

    num_args = len(args)
    if num_args == 1:
        h1 = args[0]
        return h1 == today.hour
    if num_args == 2:
        h1, h2 = args
        return h1 <= today.hour < h2
    if num_args == 4:
        h1, m1, h2, m2 = args
        return time(h1, m1) <= today.time() <= time(h2, m2)
    if num_args == 6:
        h1, m1, s1, h2, m2, s2 = args
        return time(h1, m1, s1) <= today.time() <= time(h2, m2, s2)
    return False


def alert(_):
    """No-op. PyPAC ignores JavaScript alerts."""
    pass


# Things to add to the scope of the JavaScript PAC file.
function_injections = {
    "dnsDomainIs": dnsDomainIs,
    "shExpMatch": shExpMatch,
    "isInNet": isInNet,
    "myIpAddress": myIpAddress,
    "dnsResolve": dnsResolve,
    "isPlainHostName": isPlainHostName,
    "localHostOrDomainIs": localHostOrDomainIs,
    "isResolvable": isResolvable,
    "dnsDomainLevels": dnsDomainLevels,
    "weekdayRange": weekdayRange,
    "dateRange": dateRange,
    "timeRange": timeRange,
    "alert": alert,
}
