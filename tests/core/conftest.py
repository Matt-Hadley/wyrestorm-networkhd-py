"""Fake transports for core tests.

The fakes replace only the third-party objects (paramiko's SSHClient/Channel, async_pyserial's SerialPort), so the
tests exercise the real connect(), reader task, framing and send_command() code. A device is scripted with
``replies``: command text -> list of (delay in seconds, text the device sends back).
"""

import asyncio

import pytest
import pytest_asyncio

from wyrestorm_networkhd.core import client_rs232, client_ssh
from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH

# Small timings so the suite stays fast; the client defaults are 10 s / 0.3 s
FAST = {"response_timeout": 0.5, "response_line_timeout": 0.05}


class FakeDevice:
    """State shared by every fake connection the client opens."""

    def __init__(self) -> None:
        self.replies: dict[str, list[tuple[float, str]]] = {}
        self.connect_errors: list[Exception] = []
        self.connect_attempts = 0
        self.ssh_clients: list[FakeSSHClient] = []
        self.serial_ports: list[FakeSerialPort] = []

    def reply(self, command: str, *chunks: str, delay: float = 0.0) -> None:
        """Script a reply: each chunk is sent `delay` seconds after the previous one."""
        self.replies[command] = [(delay * (i + 1), chunk) for i, chunk in enumerate(chunks)]

    @property
    def shell(self) -> "FakeShell":
        shell = self.ssh_clients[-1].shell
        assert shell is not None
        return shell

    def scheduled_replies(self, data: bytes) -> list[tuple[float, str]]:
        return self.replies.get(data.decode().rstrip("\r\n"), [])


class FakeShell:
    """paramiko.Channel stand-in. Deliberately has no send(), so only sendall() works."""

    def __init__(self, device: FakeDevice) -> None:
        self.device = device
        self.rx = bytearray()
        self.sent: list[bytes] = []
        self.closed = False
        self.max_recv = 4096
        self.timeout: float | None = None

    def feed(self, text: str) -> None:
        self.rx += text.encode()

    def recv_ready(self) -> bool:
        return bool(self.rx)

    def recv(self, nbytes: int) -> bytes:
        chunk = bytes(self.rx[: min(nbytes, self.max_recv)])
        del self.rx[: len(chunk)]
        return chunk

    def sendall(self, data: bytes) -> None:
        self.sent.append(data)
        loop = asyncio.get_running_loop()
        for delay, text in self.device.scheduled_replies(data):
            loop.call_later(delay, self.feed, text)

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout

    def close(self) -> None:
        self.closed = True


class FakeTransport:
    def __init__(self) -> None:
        self.active = True
        self.keepalive: int | None = None

    def is_active(self) -> bool:
        return self.active

    def set_keepalive(self, interval: int) -> None:
        self.keepalive = interval


class FakeSSHClient:
    """paramiko.SSHClient stand-in; connect() fails while device.connect_errors has entries."""

    def __init__(self, device: FakeDevice) -> None:
        self.device = device
        self.transport: FakeTransport | None = None
        self.shell: FakeShell | None = None
        self.closed = False
        device.ssh_clients.append(self)

    def set_missing_host_key_policy(self, _policy: object) -> None:
        pass

    def connect(self, **_kwargs: object) -> None:
        self.device.connect_attempts += 1
        if self.device.connect_errors:
            raise self.device.connect_errors.pop(0)
        self.transport = FakeTransport()

    def get_transport(self) -> FakeTransport | None:
        return self.transport

    def invoke_shell(self) -> FakeShell:
        self.shell = FakeShell(self.device)
        return self.shell

    def close(self) -> None:
        self.closed = True
        if self.transport:
            self.transport.active = False


class FakeSerialPort:
    """async_pyserial.SerialPort stand-in with the same API: open()/close()/is_open(), on(), write(data, cb)."""

    def __init__(self, device: FakeDevice, port: str, options: object) -> None:
        self.device = device
        self.port = port
        self.options = options
        self.listeners: dict[str, list] = {}
        self.opened = False
        self.written: list[bytes] = []
        device.serial_ports.append(self)

    def on(self, event: str, listener) -> None:
        self.listeners.setdefault(event, []).append(listener)

    def remove_all_listeners(self, event: str) -> None:
        self.listeners.pop(event, None)

    def emit(self, text: str) -> None:
        for listener in self.listeners.get("data", []):
            listener(text.encode())

    def open(self) -> None:
        self.device.connect_attempts += 1
        if self.device.connect_errors:
            raise self.device.connect_errors.pop(0)
        self.opened = True

    def close(self) -> None:
        self.opened = False

    def is_open(self) -> bool:
        return self.opened

    def write(self, data: bytes, callback) -> None:
        self.written.append(data)
        callback(None)
        loop = asyncio.get_running_loop()
        for delay, text in self.device.scheduled_replies(data):
            loop.call_later(delay, self.emit, text)


@pytest.fixture
def device(monkeypatch: pytest.MonkeyPatch) -> FakeDevice:
    """A scripted fake device behind both paramiko.SSHClient and async_pyserial.SerialPort."""
    fake = FakeDevice()
    monkeypatch.setattr(client_ssh.paramiko, "SSHClient", lambda: FakeSSHClient(fake))
    monkeypatch.setattr(client_rs232.async_pyserial, "SerialPort", lambda port, opts: FakeSerialPort(fake, port, opts))
    return fake


def make_ssh_client(**kwargs) -> NetworkHDClientSSH:
    return NetworkHDClientSSH(
        host="device.test",
        port=10022,
        username="user",
        password="secret",
        ssh_host_key_policy="auto_add",
        message_dispatcher_interval=0.005,
        **kwargs,
    )


@pytest_asyncio.fixture
async def ssh_client(device: FakeDevice):  # noqa: ARG001 - device patches paramiko
    """An SSH client connected to the fake device through the real connect()."""
    client = make_ssh_client()
    await client.connect()
    yield client
    await client.disconnect()


@pytest_asyncio.fixture
async def rs232_client(device: FakeDevice):  # noqa: ARG001 - device patches async_pyserial
    """An RS232 client connected to the fake device through the real connect()."""
    client = NetworkHDClientRS232(port="/dev/ttyFAKE0", baudrate=115200, message_dispatcher_interval=0.005)
    await client.connect()
    yield client
    await client.disconnect()
