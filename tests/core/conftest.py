"""Pytest configuration for core tests."""

import sys
from unittest.mock import MagicMock, AsyncMock

# Create a mock for async_pyserial module
async_pyserial_mock = MagicMock()
async_pyserial_mock.AsyncSerial = MagicMock()
async_pyserial_mock.AsyncSerial.return_value = AsyncMock()

# Add the mock to sys.modules before any imports
sys.modules['async_pyserial'] = async_pyserial_mock