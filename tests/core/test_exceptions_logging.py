"""Exception hierarchy and library logging behaviour."""

import builtins
import logging
import subprocess
import sys

import pytest

from wyrestorm_networkhd import exceptions
from wyrestorm_networkhd.logging_config import setup_logging

pytestmark = pytest.mark.unit


def test_exceptions_subclass_builtins():
    assert issubclass(exceptions.ConnectionError, builtins.ConnectionError)
    assert issubclass(exceptions.TimeoutError, builtins.TimeoutError)
    for cls in (exceptions.ConnectionLostError, exceptions.ReconnectionError):
        assert issubclass(cls, exceptions.ConnectionError)
    assert issubclass(exceptions.UnknownCommandError, exceptions.CommandError)

    error = exceptions.TimeoutError("config get version", 10.0)
    assert str(error) == "Operation 'config get version' timed out after 10.0s"
    assert isinstance(error, exceptions.NetworkHDError)


def test_import_does_not_configure_logging():
    code = (
        "import logging; root = logging.getLogger(); before = list(root.handlers);"
        "import wyrestorm_networkhd;"
        "assert root.handlers == before, root.handlers;"
        "pkg = logging.getLogger('wyrestorm_networkhd').handlers;"
        "assert [type(h).__name__ for h in pkg] == ['NullHandler'], pkg"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_setup_logging_leaves_root_handlers_alone():
    root = logging.getLogger()
    sentinel = logging.NullHandler()
    root.addHandler(sentinel)
    package_logger = logging.getLogger("wyrestorm_networkhd")
    saved = (package_logger.level, list(package_logger.handlers))
    try:
        setup_logging(level="DEBUG")
        setup_logging(level="DEBUG")

        assert sentinel in root.handlers
        assert sum(isinstance(h, logging.StreamHandler) for h in package_logger.handlers) == 1
        assert package_logger.level == logging.DEBUG
    finally:
        root.removeHandler(sentinel)
        package_logger.setLevel(saved[0])
        package_logger.handlers[:] = saved[1]
