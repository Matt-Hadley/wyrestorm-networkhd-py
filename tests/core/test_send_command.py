"""send_command() through the real reader task and framing, against a fake SSH shell."""

import asyncio
import builtins
import threading

import pytest

from wyrestorm_networkhd.exceptions import CommandError, ConnectionError, TimeoutError, UnknownCommandError

from .conftest import FAST, make_ssh_client

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_response_starts_at_echo_and_uses_sendall(ssh_client, device):
    device.reply("config get version", "config get version\r\nlib v1.2\r\n")

    response = await ssh_client.send_command("config get version", **FAST)

    assert response == "config get version\nlib v1.2"
    assert device.shell.sent == [b"config get version\n"]


async def test_line_split_across_chunks(ssh_client, device):
    device.reply("cmd", "cmd\r\nfirst li", "ne\r\nsecond line\r\n", delay=0.02)

    assert await ssh_client.send_command("cmd", **FAST) == "cmd\nfirst line\nsecond line"


async def test_small_recv_chunks_are_reassembled(ssh_client, device):
    device.shell.max_recv = 3
    device.reply("cmd", "cmd\r\nsome longer response line\r\n")

    assert await ssh_client.send_command("cmd", **FAST) == "cmd\nsome longer response line"


async def test_notification_inside_multiline_response(ssh_client, device):
    received = []
    ssh_client.register_notification_callback("endpoint", received.append)
    device.reply("cmd", "cmd\r\nline 1\r\nnotify endpoint + source1\r\nline 2\r\n")

    assert await ssh_client.send_command("cmd", **FAST) == "cmd\nline 1\nline 2"
    assert [n.device for n in received] == ["source1"]


async def test_first_line_may_take_longer_than_line_timeout(ssh_client, device):
    device.reply("slow", "slow\r\nanswer\r\n", delay=0.2)

    assert await ssh_client.send_command("slow", **FAST) == "slow\nanswer"


async def test_late_reply_does_not_leak_into_next_command(ssh_client, device):
    """Regression: the late reply to devicejsonstring landed in the device status response."""
    json_reply = 'config get devicejsonstring\r\ndevice json string: [{"aliasName": "source1"}]\r\n'
    status_reply = 'config get device status\r\ndevices status info: {"devices status": []}\r\n'
    device.reply("config get devicejsonstring")  # no reply in time
    with pytest.raises(TimeoutError):
        await ssh_client.send_command("config get devicejsonstring", response_timeout=0.1, response_line_timeout=0.05)

    # The stale reply arrives right after the next command is sent, before that command's echo
    device.reply("config get device status", json_reply + status_reply)
    response = await ssh_client.send_command("config get device status", **FAST)

    assert response == 'config get device status\ndevices status info: {"devices status": []}'


async def test_stale_lines_buffered_before_send_are_dropped(ssh_client, device):
    device.reply("cmd", "answer\r\n")  # this device does not echo
    device.shell.feed("stale line from an earlier command\r\n")

    assert await ssh_client.send_command("cmd", **FAST) == "answer"


async def test_device_without_echo_returns_all_lines(ssh_client, device):
    device.reply("cmd", "line 1\r\nline 2\r\n")

    assert await ssh_client.send_command("cmd", **FAST) == "line 1\nline 2"


async def test_welcome_banner_is_ignored(device):
    client = make_ssh_client()
    await client.connect()
    device.shell.feed("Welcome to NetworkHD\r\n")
    device.reply("cmd", "Welcome to NetworkHD\r\ncmd\r\nok\r\n")
    try:
        assert await client.send_command("cmd", **FAST) == "cmd\nok"
    finally:
        await client.disconnect()


async def test_error_response_raises_command_error(ssh_client, device):
    device.reply("cmd", "cmd\r\nERROR: bad parameter\r\n")

    with pytest.raises(CommandError, match="bad parameter"):
        await ssh_client.send_command("cmd", **FAST)


async def test_unknown_command_raises(ssh_client, device):
    device.reply("bogus", "bogus\r\nunknown command\r\n")

    with pytest.raises(UnknownCommandError) as exc_info:
        await ssh_client.send_command("bogus", **FAST)
    assert isinstance(exc_info.value, CommandError)


async def test_no_response_raises_timeout(ssh_client):
    with pytest.raises(TimeoutError) as exc_info:
        await ssh_client.send_command("silent", response_timeout=0.1, response_line_timeout=0.05)
    assert isinstance(exc_info.value, builtins.TimeoutError)
    assert ssh_client.get_connection_metrics()["commands_failed"] == 1


@pytest.mark.parametrize("command", ["cmd\nmatrix set source1 display1", "cmd\rother"])
async def test_command_with_line_break_is_rejected(ssh_client, device, command):
    with pytest.raises(CommandError, match="single line"):
        await ssh_client.send_command(command, **FAST)
    assert device.shell.sent == []


async def test_concurrent_commands_are_serialised(ssh_client, device):
    device.reply("a", "a\r\nreply a\r\n", delay=0.02)
    device.reply("b", "b\r\nreply b\r\n")

    results = await asyncio.gather(ssh_client.send_command("a", **FAST), ssh_client.send_command("b", **FAST))

    assert results == ["a\nreply a", "b\nreply b"]


@pytest.mark.usefixtures("device")
async def test_send_when_not_connected_raises():
    with pytest.raises(ConnectionError, match="Not connected"):
        await make_ssh_client().send_command("cmd")


async def test_reply_still_streaming_at_deadline_raises_timeout(ssh_client, device):
    """Regression: a reply still arriving at response_timeout was returned truncated."""
    device.reply("cmd", "cmd\r\n", *[f"line {i}\r\n" for i in range(10)], delay=0.03)

    with pytest.raises(TimeoutError):
        await ssh_client.send_command("cmd", response_timeout=0.1, response_line_timeout=0.05)


async def test_idle_gap_ending_after_deadline_still_returns(ssh_client, device):
    device.reply("cmd", "cmd\r\nok\r\n", delay=0.08)

    assert await ssh_client.send_command("cmd", response_timeout=0.1, response_line_timeout=0.05) == "cmd\nok"


async def test_reply_bytes_split_inside_a_character(ssh_client, device):
    """Regression: per-chunk decoding dropped multi-byte characters split across reads."""
    device.reply("cmd", "cmd\r\ncaf")
    task = asyncio.create_task(ssh_client.send_command("cmd", **FAST))
    await asyncio.sleep(0.02)
    device.shell.rx += b"\xc3"
    await asyncio.sleep(0.02)
    device.shell.rx += b"\xa9\r\n"

    assert await task == "cmd\ncafé"


async def test_sendall_runs_in_a_worker_thread(ssh_client, device):
    threads = []
    sendall = device.shell.sendall
    device.shell.sendall = lambda data: (threads.append(threading.get_ident()), sendall(data))
    device.reply("cmd", "cmd\r\nok\r\n")

    await ssh_client.send_command("cmd", **FAST)

    assert threads and threads[0] != threading.get_ident()
