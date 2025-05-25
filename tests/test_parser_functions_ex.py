from pypac.parser_functions_ex import getClientVersion


def test_getClientVersion():
    assert getClientVersion() == "1.0"
