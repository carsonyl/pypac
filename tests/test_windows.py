import pytest
from subprocess import CalledProcessError
from mock import patch

import sys

from pypac.windows import autoconfig_url_from_registry, NotWindowsError, ON_WINDOWS, file_url_to_local_path

test_reg_output_url = 'http://foo-bar.baz/x/proxy.pac'

not_windows = not sys.platform.startswith('win')
xfail_reason = 'not on Windows'


@pytest.mark.xfail(not_windows, reason=xfail_reason)
def test_os_detect():
    assert ON_WINDOWS


@pytest.mark.xfail(not_windows, reason=xfail_reason, raises=NotWindowsError)
def test_autoconfig_url_from_registry():
    value = autoconfig_url_from_registry()
    assert value is None or value.startswith('http://')


def _patch_winreg_qve(**kwargs):
    return patch('pypac.windows.winreg.QueryValueEx', **kwargs)


@pytest.mark.skipif(not_windows, reason=xfail_reason)
def test_mock_autoconfigurl():
    with _patch_winreg_qve(return_value=(test_reg_output_url, 'foo')):
        assert autoconfig_url_from_registry() == test_reg_output_url


@pytest.mark.skipif(not_windows, reason=xfail_reason)
def test_reg_errors_reraise():
    with _patch_winreg_qve(side_effect=WindowsError()):
        assert not autoconfig_url_from_registry()
    with _patch_winreg_qve(side_effect=CalledProcessError(2, "foo")):
        with pytest.raises(CalledProcessError) as exinfo:
            autoconfig_url_from_registry()
        assert exinfo.value.returncode == 2


@pytest.mark.parametrize('input_url,expected_path', [
    ['file://foo.pac', None],
    # UNC paths aren't local.
    [r'file://\\foo.corp.local\bar.pac', None],
    ['file:////foo.corp.local/bar.pac', None],
    ['file://///foo.corp.local/bar.pac', None],
    # urlencoded values should be decoded.
    # Assume C drive for paths starting with /.
    ['File:///foo/bar%20zip/baz.pac', 'C:/foo/bar zip/baz.pac'],
    ['file://c:/foo/bar.pac', 'c:/foo/bar.pac'],  # Drive letter OK.
])
def test_file_url_to_local_path(input_url, expected_path):
    assert file_url_to_local_path(input_url) == expected_path
