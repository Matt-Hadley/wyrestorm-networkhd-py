"""Test fixtures and utilities for core module testing - Focused on behavior testing."""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH
from wyrestorm_networkhd.models.api_notifications import NotificationObject


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def mock_notification_parser():
    """Mock notification parser for behavior testing."""
    parser = Mock()
    parser.get_notification_type.return_value = "endpoint"
    parser.parse_notification.return_value = Mock(spec=NotificationObject)
    return parser


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
    """Mock notification handler for behavior testing."""

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


@pytest.fixture
def ssh_client():
    """Create SSH client instance for testing."""
    return NetworkHDClientSSH(
        host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
    )


@pytest.fixture
def rs232_client():
    """Create RS232 client instance for testing."""
    return NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)


@pytest.fixture(params=["ssh", "rs232"])
def client(request, ssh_client, rs232_client):
    """Parametrized fixture for both client types."""
    if request.param == "ssh":
        return ssh_client
    return rs232_client


@pytest.fixture
def mock_ssh_complete():
    """Complete SSH mock setup with client, shell, and transport."""
    mock_ssh = Mock()
    mock_shell = Mock()
    mock_transport = Mock()

    # Configure all required mock behaviors
    mock_shell.closed = False
    mock_shell.recv_ready.return_value = False
    mock_shell.recv.return_value = b""
    mock_shell.send = Mock()
    mock_shell.close = Mock()
    mock_shell.settimeout = Mock()

    mock_transport.is_active.return_value = True
    mock_ssh.get_transport.return_value = mock_transport
    mock_ssh.invoke_shell.return_value = mock_shell
    mock_ssh.connect = Mock()
    mock_ssh.close = Mock()
    mock_ssh.set_missing_host_key_policy = Mock()

    return mock_ssh, mock_shell, mock_transport


@pytest.fixture
def mock_serial_complete():
    """Complete serial mock setup."""
    mock_serial = Mock()
    mock_serial.is_open = True
    mock_serial.in_waiting = 0
    mock_serial.open = AsyncMock()
    mock_serial.close = AsyncMock()
    mock_serial.read = AsyncMock(return_value=b"")
    mock_serial.write = AsyncMock()
    return mock_serial


@pytest.fixture
def mock_connected_state():
    """Fixture to mock connected state for any client."""

    def _mock_connected(client):
        if hasattr(client, "client") and hasattr(client, "shell"):
            # SSH client
            client.client = Mock()
            client.shell = Mock()
            client.shell.closed = False
            transport = Mock()
            transport.is_active.return_value = True
            client.client.get_transport.return_value = transport
        elif hasattr(client, "serial"):
            # RS232 client
            client.serial = Mock()
            client.serial.is_open = True

    return _mock_connected
