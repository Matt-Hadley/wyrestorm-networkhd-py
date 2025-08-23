"""Test fixtures and utilities for core module testing."""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.models.api_notifications import NotificationObject


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def mock_notification_parser():
    """Mock notification parser."""
    parser = Mock()
    parser.get_notification_type.return_value = "endpoint"
    parser.parse_notification.return_value = Mock(spec=NotificationObject)
    return parser


@pytest.fixture
def mock_paramiko_ssh_client():
    """Mock paramiko SSH client."""
    client = Mock()
    transport = Mock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport

    shell = Mock()
    shell.closed = False
    shell.recv_ready.return_value = False
    shell.recv.return_value = b""
    shell.send = Mock()
    shell.close = Mock()
    shell.settimeout = Mock()

    client.invoke_shell.return_value = shell
    client.connect = Mock()
    client.close = Mock()
    client.set_missing_host_key_policy = Mock()

    return client, shell, transport


@pytest.fixture
def mock_async_serial():
    """Mock async serial connection."""
    serial = Mock()
    serial.is_open = True
    serial.in_waiting = 0
    serial.open = AsyncMock()
    serial.close = AsyncMock()
    serial.read = AsyncMock(return_value=b"")
    serial.write = AsyncMock()
    return serial


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_queue() -> AsyncGenerator[asyncio.Queue, None]:
    """Create an async queue for testing."""
    queue = asyncio.Queue()
    yield queue

    # Clean up any remaining items
    while not queue.empty():
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            break


class MockNotificationHandler:
    """Mock notification handler for testing."""

    def __init__(self):
        self.callbacks = {}
        self.handle_notification = AsyncMock()

    def register_callback(self, notification_type: str, callback):
        """Register a mock callback."""
        if notification_type not in self.callbacks:
            self.callbacks[notification_type] = []
        self.callbacks[notification_type].append(callback)

    def unregister_callback(self, notification_type: str, callback):
        """Unregister a mock callback."""
        if notification_type in self.callbacks:
            try:
                self.callbacks[notification_type].remove(callback)
                if not self.callbacks[notification_type]:
                    del self.callbacks[notification_type]
            except ValueError:
                pass


@pytest.fixture
def mock_notification_handler():
    """Mock notification handler fixture."""
    return MockNotificationHandler()
