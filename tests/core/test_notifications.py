"""Notification dispatch from the reader: sync/async callbacks, errors, multi-line notifications."""

import asyncio
import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def settle() -> None:
    await asyncio.sleep(0.05)


async def test_sync_and_async_callbacks(ssh_client, device):
    received = []

    async def async_callback(notification):
        await asyncio.sleep(0)
        received.append(("async", notification.device))

    ssh_client.register_notification_callback("endpoint", lambda n: received.append(("sync", n.device)))
    ssh_client.register_notification_callback("endpoint", async_callback)
    device.shell.feed("notify endpoint + source1\r\n")
    await settle()

    assert received == [("sync", "source1"), ("async", "source1")]
    assert ssh_client.get_connection_metrics()["notifications_received"] == 1


async def test_callback_error_is_logged_and_reader_keeps_running(ssh_client, device, caplog):
    received = []

    def broken(_notification):
        raise RuntimeError("boom")

    async def broken_async(_notification):
        raise RuntimeError("async boom")

    ssh_client.register_notification_callback("endpoint", broken)
    ssh_client.register_notification_callback("endpoint", broken_async)
    ssh_client.register_notification_callback("endpoint", received.append)
    device.shell.feed("notify endpoint - display1\r\n")
    await settle()

    assert len(received) == 1
    assert "boom" in caplog.text and "async boom" in caplog.text
    assert ssh_client.is_connected()


async def test_callback_may_unregister_itself(ssh_client, device):
    calls = []

    def once(notification):
        calls.append(notification)
        ssh_client.unregister_notification_callback("endpoint", once)

    ssh_client.register_notification_callback("endpoint", once)
    device.shell.feed("notify endpoint + source1\r\nnotify endpoint + source1\r\n")
    await settle()

    assert len(calls) == 1


@pytest.mark.usefixtures("ssh_client")
async def test_unknown_notification_type_is_debug_only(device, caplog):
    caplog.set_level(logging.DEBUG, logger="wyrestorm_networkhd")
    device.shell.feed("notify somethingnew display1\r\n")
    await settle()

    records = [r for r in caplog.records if "somethingnew" in r.getMessage()]
    assert records and all(r.levelno == logging.DEBUG for r in records)


async def test_serialinfo_is_assembled_by_length(ssh_client, device):
    received = []
    ssh_client.register_notification_callback("serialinfo", received.append)
    data = "Lorem ipsum\r\ndolor sit"  # 22 characters, including a line break of its own
    device.shell.feed(f"notify serialinfo display1 ascii {len(data)}:\r\n{data[:5]}")
    await settle()
    device.shell.feed(f"{data[5:]}\r\nnotify endpoint + source1\r\n")
    await settle()

    assert len(received) == 1
    assert received[0].device == "display1"
    assert received[0].data_length == len(data)
    assert received[0].serial_data == data


async def test_hex_serialinfo_with_overstated_length_does_not_swallow_the_reply(ssh_client, device, caplog):
    caplog.set_level(logging.DEBUG)
    device.shell.feed("notify serialinfo display1 hex 500:\r\n41 42\r\n")
    await settle()
    device.reply("cmd", "cmd\r\nok\r\n")

    assert await ssh_client.send_command("cmd", response_timeout=0.5, response_line_timeout=0.05) == "cmd\nok"
    assert ssh_client._pending_serialinfo is None
    assert "data isn't hex" in caplog.text


async def test_unknown_notification_type_is_rejected(ssh_client):
    with pytest.raises(ValueError, match="Unknown notification type 'endpoints'"):
        ssh_client.register_notification_callback("endpoints", print)


async def test_irinfo_spanning_lines_is_assembled(ssh_client, device):
    received = []
    ssh_client.register_notification_callback("irinfo", received.append)
    device.shell.feed('notify irinfo display1 "0000 0067\r\n0000 0015 01FE"\r\n')
    await settle()

    assert len(received) == 1
    assert received[0].device == "display1"
    assert received[0].ir_data.split() == ["0000", "0067", "0000", "0015", "01FE"]


async def test_unterminated_irinfo_does_not_swallow_later_lines(ssh_client, device):
    """Regression: an irinfo header without a closing quote made the client join every later line onto it."""
    irinfo, endpoint = [], []
    ssh_client.register_notification_callback("irinfo", irinfo.append)
    ssh_client.register_notification_callback("endpoint", endpoint.append)
    device.shell.feed('notify irinfo display1 "0000 0067\r\n0000 0015\r\nnotify endpoint + source1\r\n')
    await settle()

    assert [n.device for n in endpoint] == ["source1"]
    assert irinfo == []  # handed over incomplete; the parser rejects the unclosed quote (logged)
    device.reply("cmd", "cmd\r\nok\r\n")
    assert await ssh_client.send_command("cmd", response_timeout=0.5, response_line_timeout=0.05) == "cmd\nok"


async def test_serialinfo_length_counts_bytes(ssh_client, device):
    """Regression: <infolen> was counted in decoded characters, so multi-byte data was cut wrongly."""
    received = []
    ssh_client.register_notification_callback("serialinfo", received.append)
    data = "café"  # 5 bytes in UTF-8
    device.shell.feed(f"notify serialinfo display1 ascii 5:\r\n{data}notify endpoint + source1\r\n")
    await settle()

    assert [n.serial_data for n in received] == [data]


async def test_serialinfo_data_ending_in_line_break_needs_no_extra_one(ssh_client, device):
    received, endpoint = [], []
    ssh_client.register_notification_callback("serialinfo", received.append)
    ssh_client.register_notification_callback("endpoint", endpoint.append)
    device.shell.feed("notify serialinfo display1 ascii 4:\r\nab\r\nnotify endpoint + source1\r\n")
    await settle()

    assert [n.serial_data.rstrip() for n in received] == ["ab"]
    assert [n.device for n in endpoint] == ["source1"]


async def test_serialinfo_is_dispatched_without_waiting_for_line_break(ssh_client, device):
    received = []
    ssh_client.register_notification_callback("serialinfo", received.append)
    device.shell.feed("notify serialinfo display1 ascii 2:\r\nab\r")
    await settle()
    assert [n.serial_data for n in received] == ["ab"]
    device.shell.feed("\n")  # the late line break is just an empty line
    await settle()
    assert [n.serial_data for n in received] == ["ab"]


async def test_serialinfo_data_followed_directly_by_notifications(ssh_client, device):
    """Regression: data not followed by a line break was dropped, and the next line with it."""
    serial, endpoint = [], []
    ssh_client.register_notification_callback("serialinfo", serial.append)
    ssh_client.register_notification_callback("endpoint", endpoint.append)
    device.shell.feed("notify serialinfo display1 hex 5:\r\n41 42")
    await settle()
    device.shell.feed("notify endpoint + source1\r\nnotify endpoint + source2\r\n")
    await settle()

    assert [n.serial_data for n in serial] == ["41 42"]
    assert [n.device for n in endpoint] == ["source1", "source2"]


@pytest.mark.parametrize("length", ["65537", "1" * 200])
async def test_serialinfo_with_oversized_length_is_not_framed(ssh_client, device, length, caplog):
    serial, endpoint = [], []
    ssh_client.register_notification_callback("serialinfo", serial.append)
    ssh_client.register_notification_callback("endpoint", endpoint.append)
    device.shell.feed(f"notify serialinfo display1 ascii {length}:\r\nab\r\nnotify endpoint + source1\r\n")
    await settle()

    assert serial == []
    assert ssh_client._pending_serialinfo is None
    assert [n.device for n in endpoint] == ["source1"]
    assert "oversized length" in caplog.text


async def test_serialinfo_at_length_cap_is_assembled(ssh_client, device):
    received = []
    ssh_client.register_notification_callback("serialinfo", received.append)
    data = "x" * 65536
    device.shell.feed(f"notify serialinfo display1 ascii {len(data)}:\r\n{data}\r\n")
    await asyncio.sleep(0.2)

    assert [len(n.serial_data) for n in received] == [len(data)]


async def test_endless_line_is_dropped(ssh_client, device, caplog):
    endpoint = []
    ssh_client.register_notification_callback("endpoint", endpoint.append)
    for _ in range(4):
        device.shell.feed("notify endpoint + " + "y" * 40000)
        await settle()
    assert len(ssh_client._buffer) <= 65536
    device.shell.feed("tail\r\nnotify endpoint + source1\r\n")
    await settle()

    assert [n.device for n in endpoint] == ["source1"]
    assert "without a line break" in caplog.text


async def test_long_line_in_one_read_is_dropped(ssh_client, caplog):
    ssh_client._feed(b"z" * 70000 + b"\r\nnotify endpoint + source1\r\n")
    endpoint = []
    ssh_client.register_notification_callback("endpoint", endpoint.append)
    ssh_client._feed(b"notify endpoint + source2\r\n")

    assert [n.device for n in endpoint] == ["source2"]
    assert "Dropping 70001-byte line" in caplog.text


async def test_unterminated_irinfo_is_capped(ssh_client, device):
    irinfo = []
    ssh_client.register_notification_callback("irinfo", irinfo.append)
    device.shell.feed('notify irinfo display1 "0000\r\n' + "0000 0067\r\n" * 8000)
    await settle()

    assert ssh_client._pending_irinfo is None or len(ssh_client._pending_irinfo) < 65536
