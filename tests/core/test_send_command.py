"""send_command() through the real reader task and framing, against a fake SSH shell."""

import asyncio
import builtins
import threading

import pytest

from wyrestorm_networkhd.core._client import _is_foreign_echo
from wyrestorm_networkhd.exceptions import CommandError, ConnectionError, TimeoutError, UnknownCommandError
from wyrestorm_networkhd.models.api_query import DeviceStatus, Matrix

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


# The controller echoes every API session's commands and replies to all sessions. These replay another client's
# `config get version` / `config get devicejsonstring` traffic (seen on an NHD-000-CTL, firmware 9.4.13) around ours.
STATUS_REPLY = (
    "config get device status\r\n"
    'devices status info:\r\n{\r\n"devices status" : [\r\n{"aliasname" : "DISPLAY1", "name" : "NHD-RX-1"}\r\n]\r\n}\r\n'
)
FOREIGN_JSON = (
    "config get devicejsonstring\r\n"
    'devices json info:\r\n{\r\n"devices" : [\r\n{"aliasname" : "SOURCE1", "name" : "NHD-TX-1"}\r\n]\r\n}\r\n'
)
FOREIGN_VERSION = "config get version\r\nAPI version: v1.21\r\nSystem version: v9.4.13(v2.0.0)\r\n"


async def test_foreign_session_burst_after_our_reply_is_dropped(ssh_client, device):
    device.reply("config get device status", STATUS_REPLY + FOREIGN_VERSION + FOREIGN_JSON)
    device.reply("matrix get", "matrix get\r\nmatrix information:\r\nsource1 display1\r\n")

    response = await ssh_client.send_command("config get device status", **FAST)

    assert response == STATUS_REPLY.replace("\r\n", "\n").strip()
    assert [d.aliasname for d in DeviceStatus.parse(response)] == ["DISPLAY1"]
    # Nothing of the foreign burst reaches the next command
    assert await ssh_client.send_command("matrix get", **FAST) == "matrix get\nmatrix information:\nsource1 display1"


@pytest.mark.parametrize("gap", [0.0, 0.1], ids=["back-to-back", "idle-gap-before-our-echo"])
async def test_foreign_session_burst_before_our_echo_is_dropped(ssh_client, device, gap):
    # With a gap longer than response_line_timeout, the foreign burst alone used to be taken as the response
    device.reply("config get device status", FOREIGN_JSON, STATUS_REPLY, delay=gap)

    response = await ssh_client.send_command("config get device status", **FAST)

    assert [d.aliasname for d in DeviceStatus.parse(response)] == ["DISPLAY1"]


async def test_foreign_echo_without_ours_times_out(ssh_client, device):
    device.reply("config get device status", FOREIGN_JSON)

    with pytest.raises(TimeoutError):
        await ssh_client.send_command("config get device status", **FAST)


async def test_foreign_burst_during_matrix_get(ssh_client, device):
    device.reply(
        "matrix get", "matrix get\r\nmatrix information:\r\nsource1 display1\r\nNULL display2\r\n" + FOREIGN_VERSION
    )

    matrix = Matrix.parse(await ssh_client.send_command("matrix get", **FAST))

    assert [(a.tx, a.rx) for a in matrix.assignments] == [("source1", "display1"), (None, "display2")]


async def test_notifications_in_foreign_burst_are_dispatched(ssh_client, device):
    received = []
    ssh_client.register_notification_callback("endpoint", received.append)
    device.reply(
        "matrix get",
        "matrix get\r\nnotify endpoint + source1\r\nmatrix information:\r\nsource1 display1\r\n"
        "config get version\r\nnotify endpoint - source2\r\nAPI version: v1.21\r\n",
    )

    assert await ssh_client.send_command("matrix get", **FAST) == "matrix get\nmatrix information:\nsource1 display1"
    assert [n.device for n in received] == ["source1", "source2"]


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
        ("mscene active display1 grid failure", False),
        ("display1's alias is DISPLAY1", False),
        ("source1 display1", False),
        ("API version: v1.21", False),
    ],
)
def test_is_foreign_echo(line, foreign):
    assert _is_foreign_echo(line, "matrix get") is foreign
