import pytest
from subprocess import CalledProcessError
from mock import patch

import sys

from pypac.windows import autoconfig_url_from_registry, NotWindowsError, ON_WINDOWS

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
