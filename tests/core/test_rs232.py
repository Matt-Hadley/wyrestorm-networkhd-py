"""RS232 client against a fake async_pyserial.SerialPort (same API as the real one)."""

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.exceptions import ConnectionLostError

from .conftest import FAST

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_send_command_writes_crlf_and_reads_reply(rs232_client, device):
    device.reply("config get version", "config get ver", "sion\r\nAPI version: v1.0\r\n", delay=0.01)

    response = await rs232_client.send_command("config get version", **FAST)

    assert response == "config get version\nAPI version: v1.0"
    assert device.serial_ports[-1].written == [b"config get version\r\n"]


async def test_serial_options_are_passed(device):
    client = NetworkHDClientRS232(port="/dev/ttyFAKE0", baudrate=115200, stopbits=2)
    await client.connect()
    try:
        port = device.serial_ports[-1]
        assert port.port == "/dev/ttyFAKE0"
        assert (port.options.baudrate, port.options.stopbits) == (115200, 2)
        assert client.is_connected()
    finally:
        await client.disconnect()


async def test_disconnect_clears_serial(rs232_client, device):
    await rs232_client.disconnect()

    assert rs232_client.serial is None
    assert not device.serial_ports[-1].is_open()
    assert not rs232_client.is_connected()
    assert rs232_client.get_connection_state() == "disconnected"


async def test_port_closed_underneath_is_not_connected(rs232_client, device):
    device.serial_ports[-1].close()

    assert not rs232_client.is_connected()
    assert rs232_client.get_connection_state() == "disconnected"


async def test_failed_write_marks_connection_lost(rs232_client, device):
    """Regression: a serial write failure left the client 'connected'."""
    device.serial_ports[-1].write = lambda _data, callback: callback(OSError("device not configured"))

    with pytest.raises(OSError):
        await rs232_client.send_command("cmd", **FAST)

    assert not rs232_client.is_connected()
    assert rs232_client.get_connection_state() == "error"
    with pytest.raises(ConnectionLostError):
        await rs232_client.send_command("cmd", **FAST)
