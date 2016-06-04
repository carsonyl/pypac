import pytest
from subprocess import CalledProcessError
from mock import patch

import sys

from pypac.windows import on_windows, autoconfig_url_from_registry, NotWindowsError, parse_reg_output

test_reg_output = b"""
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings
    AutoConfigURL    REG_SZ    http://foo-bar.baz/x/proxy.pac


"""
test_reg_output_url = 'http://foo-bar.baz/x/proxy.pac'

not_windows = not sys.platform.startswith('win')
xfail_reason = 'not on Windows'


@pytest.mark.xfail(not_windows, reason=xfail_reason)
def test_os_detect():
    assert on_windows()


@pytest.mark.xfail(not_windows, reason=xfail_reason, raises=NotWindowsError)
def test_autoconfig_url_from_registry():
    value = autoconfig_url_from_registry()
    assert value is None or value.startswith('http://')


def _patch_check_output(**kwargs):
    return patch('pypac.windows.check_output', **kwargs)


@pytest.mark.skipif(not_windows, reason=xfail_reason)
def test_mock_autoconfigurl():
    with _patch_check_output(return_value=test_reg_output):
        assert autoconfig_url_from_registry() == test_reg_output_url


@pytest.mark.skipif(not_windows, reason=xfail_reason)
def test_reg_errors_reraise():
    with _patch_check_output(side_effect=CalledProcessError(1, "foo")):
        assert not autoconfig_url_from_registry()
    with _patch_check_output(side_effect=CalledProcessError(2, "foo")):
        with pytest.raises(CalledProcessError) as exinfo:
            autoconfig_url_from_registry()
        assert exinfo.value.returncode == 2


def test_parse_reg_output():
    assert parse_reg_output(test_reg_output) == test_reg_output_url
