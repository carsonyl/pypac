import pytest
from subprocess import CalledProcessError

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import sys

from pypac.os_settings import (
    autoconfig_url_from_registry,
    autoconfig_url_from_preferences,
    NotWindowsError,
    NotDarwinError,
    ON_WINDOWS,
    ON_DARWIN,
    file_url_to_local_path,
)

test_reg_output_url = "http://foo-bar.baz/x/proxy.pac"

not_windows = not sys.platform.startswith("win")
not_darwin = not (sys.platform == "darwin")
windows_reason = "not on Windows"
darwin_reason = "not on macOS/OSX"


@pytest.mark.xfail(not_windows, reason=windows_reason)
def test_os_detect_windows():
    assert ON_WINDOWS


@pytest.mark.xfail(not_darwin, reason=darwin_reason)
def test_os_detect_darwin():
    assert ON_DARWIN


@pytest.mark.xfail(not_windows, reason=windows_reason, raises=NotWindowsError)
def test_autoconfig_url_from_registry():
    value = autoconfig_url_from_registry()
    assert value is None or value.startswith("http://")


@pytest.mark.xfail(not_darwin, reason=darwin_reason, raises=NotDarwinError)
def test_autoconfig_url_from_preferences():
    value = autoconfig_url_from_preferences()
    assert value is None or value.startswith("http://")


def _patch_winreg_qve(**kwargs):
    return patch("pypac.os_settings.winreg.QueryValueEx", **kwargs)


@pytest.mark.skipif(not_windows, reason=windows_reason)
def test_mock_autoconfigurl_windows():
    with _patch_winreg_qve(return_value=(test_reg_output_url, "foo")):
        assert autoconfig_url_from_registry() == test_reg_output_url


def _patch_pyobjc_dscp(**kwargs):
    return patch("pypac.os_settings.SystemConfiguration.SCDynamicStoreCopyProxies", **kwargs)


@pytest.mark.skipif(not_darwin, reason=darwin_reason)
def test_mock_autoconfigurl_mac():
    with _patch_pyobjc_dscp(return_value={"ProxyAutoConfigEnable": 1, "ProxyAutoConfigURLString": test_reg_output_url}):
        assert autoconfig_url_from_preferences() == test_reg_output_url


@pytest.mark.skipif(not_windows, reason=windows_reason)
def test_reg_errors_reraise():
    with _patch_winreg_qve(side_effect=WindowsError()):
        assert not autoconfig_url_from_registry()
    with _patch_winreg_qve(side_effect=CalledProcessError(2, "foo")):
        with pytest.raises(CalledProcessError) as exinfo:
            autoconfig_url_from_registry()
        assert exinfo.value.returncode == 2


@pytest.mark.skipif(not_darwin, reason=darwin_reason)
def test_reg_errors_reraise():
    with _patch_pyobjc_dscp(side_effect=AttributeError()):
        assert not autoconfig_url_from_preferences()
    with _patch_pyobjc_dscp(side_effect=CalledProcessError(2, "foo")):
        with pytest.raises(CalledProcessError) as exinfo:
            autoconfig_url_from_preferences()
        assert exinfo.value.returncode == 2


@pytest.mark.parametrize(
    "input_url,windows_expected_path,mac_expected_path",
    [
        ["file://foo.pac", None, None],
        # UNC paths aren't local.
        [r"file://\\foo.corp.local\bar.pac", None, None],
        ["file:////foo.corp.local/bar.pac", None, None],
        ["file://///foo.corp.local/bar.pac", None, None],
        # urlencoded values should be decoded.
        # Assume C drive for paths starting with /.
        ["File:///foo/bar%20zip/baz.pac", "C:/foo/bar zip/baz.pac", "/foo/bar zip/baz.pac"],
        ["file://c:/foo/bar.pac", "c:/foo/bar.pac", "/foo/bar.pac"],
    ],
)
def test_file_url_to_local_path(input_url, windows_expected_path, mac_expected_path):
    if ON_WINDOWS:
        expected_path = windows_expected_path
    elif ON_DARWIN:
        expected_path = mac_expected_path
    else:
        pytest.skip("Not on Windows or macOS/OSX")
    assert file_url_to_local_path(input_url) == expected_path
