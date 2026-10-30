"""Connection lifecycle: connect, disconnect, link loss, reconnect, constructor arguments."""

import asyncio

import paramiko
import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH
from wyrestorm_networkhd.exceptions import (
    AuthenticationError,
    ConnectionError,
    ConnectionLostError,
    ReconnectionError,
)

from .conftest import FAST, make_ssh_client

pytestmark = pytest.mark.unit


async def wait_until(condition, timeout: float = 1.0) -> None:
    async with asyncio.timeout(timeout):
        while not condition():
            await asyncio.sleep(0.005)


@pytest.mark.asyncio
async def test_connect_sets_keepalive_and_starts_reader(ssh_client, device):
    assert ssh_client.is_connected()
    assert ssh_client.get_connection_state() == "connected"
    assert device.ssh_clients[-1].transport.keepalive == 30
    assert device.shell.timeout == 10.0
    assert not ssh_client._message_dispatcher_task.done()


@pytest.mark.asyncio
async def test_connect_tears_down_previous_connection(ssh_client, device):
    first_client, first_task = device.ssh_clients[-1], ssh_client._message_dispatcher_task

    await ssh_client.connect()

    assert first_client.closed and first_client.shell.closed
    assert first_task.done()
    assert len(device.ssh_clients) == 2
    device.reply("cmd", "cmd\r\nok\r\n")
    assert await ssh_client.send_command("cmd", **FAST) == "cmd\nok"


@pytest.mark.asyncio
async def test_disconnect(ssh_client, device):
    await ssh_client.disconnect()

    assert device.ssh_clients[-1].closed
    assert ssh_client.client is None and ssh_client.shell is None
    assert ssh_client._message_dispatcher_task is None
    assert not ssh_client.is_connected()
    assert ssh_client.get_connection_state() == "disconnected"


@pytest.mark.asyncio
@pytest.mark.usefixtures("device")
async def test_context_manager():
    async with make_ssh_client() as client:
        assert client.is_connected()
    assert not client.is_connected()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (paramiko.AuthenticationException("bad password"), AuthenticationError),
        (paramiko.SSHException("protocol error"), ConnectionError),
        (OSError("connection refused"), ConnectionError),
    ],
)
async def test_connect_failure(device, error, expected):
    device.connect_errors = [error]
    client = make_ssh_client()

    with pytest.raises(expected):
        await client.connect()

    assert not client.is_connected()
    assert client.get_connection_state() == "error"
    assert client._message_dispatcher_task is None


@pytest.mark.asyncio
async def test_link_loss_marks_disconnected_and_next_send_raises(ssh_client, device):
    device.shell.closed = True

    await wait_until(lambda: ssh_client._message_dispatcher_task is None)

    assert not ssh_client.is_connected()
    assert ssh_client.get_connection_state() == "error"
    with pytest.raises(ConnectionLostError) as exc_info:
        await ssh_client.send_command("cmd", **FAST)
    assert isinstance(exc_info.value, ConnectionError)


@pytest.mark.asyncio
async def test_link_loss_while_waiting_fails_the_command(ssh_client, device):
    asyncio.get_running_loop().call_later(0.05, setattr, device.shell, "closed", True)

    with pytest.raises(ConnectionLostError):
        await ssh_client.send_command("cmd", response_timeout=2.0, response_line_timeout=0.05)


@pytest.mark.asyncio
async def test_reconnect_retries_until_connected(ssh_client, device):
    device.shell.closed = True
    await wait_until(lambda: not ssh_client.is_connected())
    device.connect_attempts = 0
    device.connect_errors = [OSError("unreachable"), paramiko.SSHException("banner timeout")]

    await ssh_client.reconnect(max_attempts=5, delay=0.001)

    assert device.connect_attempts == 3
    assert ssh_client.is_connected()
    assert not ssh_client._message_dispatcher_task.done()
    device.reply("cmd", "cmd\r\nok\r\n")
    assert await ssh_client.send_command("cmd", **FAST) == "cmd\nok"


@pytest.mark.asyncio
async def test_reconnect_gives_up_with_reconnection_error(device):
    device.connect_errors = [OSError("unreachable")] * 3
    client = make_ssh_client()

    with pytest.raises(ReconnectionError) as exc_info:
        await client.reconnect(max_attempts=3, delay=0.001)

    assert device.connect_attempts == 3
    assert exc_info.value.attempts == 3
    assert isinstance(exc_info.value, ConnectionError)


@pytest.mark.asyncio
async def test_reconnect_does_not_retry_bad_credentials(device):
    device.connect_errors = [paramiko.AuthenticationException("bad password")] * 3

    with pytest.raises(AuthenticationError):
        await make_ssh_client().reconnect(max_attempts=3, delay=0.001)
    assert device.connect_attempts == 1


@pytest.mark.asyncio
async def test_concurrent_reconnect_waits_instead_of_returning(device):
    device.connect_errors = [OSError("unreachable")]
    client = make_ssh_client()

    await asyncio.gather(client.reconnect(max_attempts=3, delay=0.01), client.reconnect(max_attempts=3, delay=0.01))

    assert client.is_connected()
    assert device.connect_attempts == 2  # the second caller reused the first caller's connection
    await client.disconnect()


@pytest.mark.parametrize("name", ["heartbeat_interval", "circuit_breaker_timeout"])
def test_removed_arguments_are_deprecated(name):
    with pytest.warns(DeprecationWarning, match=name):
        make_ssh_client(**{name: 30.0})
    with pytest.warns(DeprecationWarning, match=name):
        NetworkHDClientRS232(port="/dev/ttyFAKE0", baudrate=9600, **{name: 30.0})


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"host": ""}, "Host is required"),
        ({"port": 0}, "Port must be an integer"),
        ({"username": ""}, "Username is required"),
        ({"password": ""}, "Password is required"),
        ({"timeout": 0}, "Timeout must be positive"),
        ({"ssh_host_key_policy": "trust"}, "Invalid ssh_host_key_policy"),
        ({"message_dispatcher_interval": 0}, "Message dispatcher interval must be positive"),
    ],
)
def test_ssh_validation(kwargs, message):
    args = {"host": "device.test", "port": 10022, "username": "u", "password": "p", "ssh_host_key_policy": "warn"}
    with pytest.raises(ValueError, match=message):
        NetworkHDClientSSH(**{**args, **kwargs})


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"port": ""}, "Port is required"),
        ({"baudrate": 0}, "Baudrate must be a positive integer"),
        ({"timeout": -1}, "Timeout must be positive"),
        ({"flow_control": True}, "Unknown serial options: flow_control"),
    ],
)
def test_rs232_validation(kwargs, message):
    with pytest.raises(ValueError, match=message):
        NetworkHDClientRS232(**{"port": "/dev/ttyFAKE0", "baudrate": 9600, **kwargs})
