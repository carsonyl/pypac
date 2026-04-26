from subprocess import CalledProcessError

import pytest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import sys

from pypac.os_settings import (
    ON_DARWIN,
    ON_WINDOWS,
    NotDarwinError,
    NotWindowsError,
    autoconfig_url_from_preferences,
    autoconfig_url_from_registry,
    file_url_to_local_path,
)

HKEY_CURRENT_MACHINE = 0
HKEY_CURRENT_USER = 1
if ON_WINDOWS:
    try:
        import winreg
    except ImportError:  # PY2.
        import _winreg as winreg  # type: ignore
    HKEY_CURRENT_MACHINE = winreg.HKEY_LOCAL_MACHINE
    HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER

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
@pytest.mark.parametrize(
    "openkey_success, qve_value, expected",
    [
        pytest.param(False, None, True, id="absent-key"),
        pytest.param(True, (1, 4), True, id="per-user"),  # ProxySettingsPerUser=1
        pytest.param(True, (0, 4), False, id="per-machine"),  # ProxySettingsPerUser=0
    ],
)
def test_is_per_user_proxy_setting(openkey_success, qve_value, expected):
    """_is_per_user_proxy_setting returns expected bool based on registry state."""
    with patch("pypac.os_settings.winreg.OpenKey") as mock_openkey:
        if openkey_success:
            mock_openkey.return_value.__enter__.return_value = mock_openkey.return_value
        else:
            mock_openkey.side_effect = WindowsError()
        with patch("pypac.os_settings.winreg.QueryValueEx", return_value=qve_value):
            from pypac.os_settings import _is_per_user_proxy_setting

            assert _is_per_user_proxy_setting() is expected


@pytest.mark.skipif(not_windows, reason=windows_reason)
@pytest.mark.parametrize(
    "per_user, expected_hive",
    [
        pytest.param(True, HKEY_CURRENT_USER, id="per-user"),
        pytest.param(False, HKEY_CURRENT_MACHINE, id="per-machine"),
    ],
)
def test_autoconfig_url_from_registry_mode(per_user, expected_hive):
    """autoconfig_url_from_registry checks the correct hive in per-user and per-machine mode."""
    with patch("pypac.os_settings._is_per_user_proxy_setting", return_value=per_user):
        with patch("pypac.os_settings.winreg.OpenKey") as mock_openkey:
            mock_openkey.return_value.__enter__.return_value = mock_openkey.return_value
            with _patch_winreg_qve(return_value=(test_reg_output_url, "foo")):
                assert autoconfig_url_from_registry() == test_reg_output_url
            mock_openkey.assert_called_once()
            assert mock_openkey.call_args[0][0] == expected_hive


@pytest.mark.skipif(not_windows, reason=windows_reason)
def test_per_machine_mode_no_fallback_to_hkcu():
    """In per-machine mode, when HKLM has no AutoConfigURL, return None without checking HKCU."""
    with patch("pypac.os_settings._is_per_user_proxy_setting", return_value=False):
        with patch("pypac.os_settings.winreg.OpenKey") as mock_openkey:
            mock_openkey.return_value.__enter__.return_value = mock_openkey.return_value
            with _patch_winreg_qve(side_effect=WindowsError()):
                assert autoconfig_url_from_registry() is None
            mock_openkey.assert_called_once()
            assert mock_openkey.call_args[0][0] == HKEY_CURRENT_MACHINE


def _patch_pyobjc_dscp(**kwargs):
    return patch("pypac.os_settings.SystemConfiguration.SCDynamicStoreCopyProxies", **kwargs)


@pytest.mark.skipif(not_darwin, reason=darwin_reason)
def test_mock_autoconfigurl_mac():
    with _patch_pyobjc_dscp(return_value={"ProxyAutoConfigEnable": 1, "ProxyAutoConfigURLString": test_reg_output_url}):
        assert autoconfig_url_from_preferences() == test_reg_output_url


@pytest.mark.skipif(not_windows, reason=windows_reason)
def test_reg_errors_reraise_win():
    with patch("pypac.os_settings._is_per_user_proxy_setting", return_value=True):
        with _patch_winreg_qve(side_effect=WindowsError()):
            assert not autoconfig_url_from_registry()
    with patch("pypac.os_settings._is_per_user_proxy_setting", return_value=True):
        with _patch_winreg_qve(side_effect=CalledProcessError(2, "foo")):
            with pytest.raises(CalledProcessError) as exinfo:
                autoconfig_url_from_registry()
            assert exinfo.value.returncode == 2


@pytest.mark.skipif(not_darwin, reason=darwin_reason)
def test_reg_errors_reraise_mac():
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
        return
    assert file_url_to_local_path(input_url) == expected_path
