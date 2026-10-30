"""Recognising another API session's command echo (synchronous, so kept out of the async-marked modules)."""

import pytest

from wyrestorm_networkhd.core._client import _is_foreign_echo

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("line", "foreign"),
    [
        ("config get devicejsonstring", True),
        ("config get version", True),
        ("matrix get display1", True),  # differs from our "matrix get"
        ("matrix get", False),  # our own echo
        ("matrix information:", False),
        ("matrix video information:", False),
        ("scene list:", False),
        ("mscene list:", False),
        ("devices json info:", False),
        ("scene OfficeVW-Splitmode active success", False),
        ("scene OfficeVW-Splitmode's source in [1,2] change to source1", False),
        ("mscene active display1 grid failure", False),
        ("display1's alias is DISPLAY1", False),
        ("source1 display1", False),
        ("API version: v1.21", False),
    ],
)
def test_is_foreign_echo(line, foreign):
    assert _is_foreign_echo(line, "matrix get") is foreign
