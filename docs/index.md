# 🌊 WyreStorm NetworkHD Python Client

[![PyPI version](https://badge.fury.io/py/wyrestorm-networkhd.svg)](https://badge.fury.io/py/wyrestorm-networkhd)
[![Python Support](https://img.shields.io/pypi/pyversions/wyrestorm-networkhd.svg)](https://pypi.org/project/wyrestorm-networkhd/)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Matt-Hadley/8f4a6e65e2d520f63a82a34cddcc4b56/raw/coverage.json)](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An async Python client for WyreStorm NetworkHD AV-over-IP systems. It talks to the NetworkHD controller over SSH or
RS232, wraps the NetworkHD API in typed methods and response models, and delivers real-time notifications to your
callbacks.

Upgrading from 2.x? Read [Migrating from 2.x to 3.0](migration.md).

## 🖥️ Supported Hardware

- **Controllers:** NHD-000-CTL and NHD-CTL-PRO, as covered by the NetworkHD API v6.7 document on the
  [Resources](resources.md) page. The library talks to the controller only, never to endpoints directly.
- **Endpoints:** the 100, 200, 400, 500 and 600 series encoders and decoders that the API document covers. Some commands
  apply to certain series only; each method's docstring lists them.
- **Tested on:** NHD-000-CTL firmware v9.4.7 (API v1.28) with NHD-400 TX/RX firmware v2.5.6, over SSH.
- **Connection:** SSH (port 10022) or RS232. The controller ships with only Telnet enabled, which this library does not
  support: enable SSH in the controller's web interface first. The default SSH credentials are `wyrestorm` /
  `networkhd`.

## 📦 Installation

```bash
pip install wyrestorm-networkhd

# With RS232 support
pip install "wyrestorm-networkhd[rs232]"
```

Requires Python 3.11 or later.

## 🚀 Quick Start

This example connects over SSH, listens for notifications, and reads from the controller without changing anything:

```python
import asyncio

from wyrestorm_networkhd import NHDAPI, NetworkHDClientSSH, NetworkHDError


def on_endpoint(notification):
    print(f"{notification.device} is {'online' if notification.online else 'offline'}")


async def on_video(notification):
    # Callbacks may be plain functions or coroutine functions
    print(f"{notification.device}: video {notification.status}")


async def main():
    client = NetworkHDClientSSH(
        host="192.168.1.100",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn",
    )
    client.register_notification_callback("endpoint", on_endpoint)
    client.register_notification_callback("video", on_video)

    try:
        async with client:
            api = NHDAPI(client)

            print(await api.api_query.config_get_version())

            for device in await api.api_query.config_get_device_info():
                print(f"{device.aliasname} ({device.name}): {device.ip4addr}")

            for status in await api.api_query.config_get_device_status():
                print(f"{status.aliasname}: HDMI out active = {status.hdmi_out_active}")

            matrix = await api.api_query.matrix_get()
            for assignment in matrix.assignments:
                print(f"{assignment.rx} <- {assignment.tx}")

            # Keep the connection open for a while to receive notifications
            await asyncio.sleep(30)
    except NetworkHDError as e:
        print(f"NetworkHD error: {e}")


asyncio.run(main())
```

## 📋 API Categories

`NHDAPI` groups the commands the same way as the chapters of the API document. See the
[Commands reference](reference/commands.md) for every method.

| Attribute                    | Covers                                                    |
| ---------------------------- | --------------------------------------------------------- |
| `api_query`                  | System, device, matrix, video wall and multiview queries  |
| `api_endpoint`               | Session alias mode                                        |
| `api_notifications`          | Enabling and disabling notifications                      |
| `media_stream_matrix_switch` | Video, audio, USB, infrared and RS232 routing             |
| `device_port_switch`         | Input and port selection on endpoints                     |
| `connected_device_control`   | CEC, infrared, RS232 and sink power for connected devices |
| `audio_output`               | Analog audio volume                                       |
| `video_wall`                 | Video wall scenes, logical screens and windows            |
| `multiview`                  | Preset and custom multiview layouts                       |
| `video_stream_text_overlay`  | On-screen text overlay                                    |
| `reboot_reset`               | Rebooting and resetting devices                           |

## 🔗 Connections

### SSH

```python
from wyrestorm_networkhd import NetworkHDClientSSH

client = NetworkHDClientSSH(
    host="192.168.1.100",
    port=10022,
    username="wyrestorm",
    password="networkhd",
    ssh_host_key_policy="warn",  # "auto_add", "warn" or "reject": see SSH host keys below
    timeout=10.0,  # connect timeout in seconds
)
```

The client sends an SSH keepalive every 30 seconds so a dead link is noticed and NAT/firewall state is kept.

### RS232

```python
from wyrestorm_networkhd import NetworkHDClientRS232

client = NetworkHDClientRS232(
    port="/dev/ttyUSB0",  # "COM3" on Windows
    baudrate=9600,  # the controller's RS232 port runs at 9600 8N1
    timeout=10.0,  # write timeout in seconds
)
```

`NetworkHDClientRS232` needs the `rs232` extra (`pip install "wyrestorm-networkhd[rs232]"`) and permission to open the
serial port. Extra keyword arguments are passed to async-pyserial's `SerialPortOptions` (`bytesize`, `stopbits`,
`parity`, `read_timeout`, `write_timeout`, `read_bufsize`); any other name raises `ValueError`.

### Timeouts

`send_command()`, which every `NHDAPI` method uses, takes two timeouts:

- `response_timeout` (default 10 s): the most the whole reply may take. If nothing arrives, or lines are still arriving
  when it expires, it raises `TimeoutError` rather than returning a truncated reply.
- `response_line_timeout` (default 0.3 s): the reply ends when no further line arrives for this long. Raise it for slow,
  multi-line replies.

```python
response = await client.send_command("config get version", response_timeout=5.0, response_line_timeout=0.5)
```

Both clients also accept `message_dispatcher_interval` (default 0.1 s for SSH, 0.05 s for RS232): how long the reader
sleeps when nothing is readable.

### Reconnecting

When the link drops, `is_connected()` returns `False` and the next command raises `ConnectionLostError`. Call
`reconnect()` to connect again:

```python
from wyrestorm_networkhd import ConnectionLostError, ReconnectionError

try:
    matrix = await api.api_query.matrix_get()
except ConnectionLostError:
    try:
        await client.reconnect(max_attempts=5, delay=1.0)
    except ReconnectionError as e:
        print(f"Gave up after {e.attempts} attempts: {e.last_error}")
```

`reconnect()` also works from any other state, for example after `disconnect()`. It waits `delay` seconds before the
second attempt and doubles it each time, capped at 30 seconds, with jitter. It raises `ReconnectionError` when every
attempt fails, and `AuthenticationError` or `HostKeyMismatchError` at once if the credentials or the host key are
rejected.

### SSH Host Keys

`ssh_host_key_policy` is required, so you choose how the controller's host key is checked:

- `"auto_add"` and `"warn"` accept **any** host key, on every connection: the library keeps no record of keys between
  connections. `"warn"` also emits a Python warning. Both are open to a man-in-the-middle on the network between you and
  the controller.
- `"reject"` refuses any host key that is not already known. The library doesn't load a `known_hosts` file, so in 3.0
  `"reject"` refuses every controller.

To protect against that, pin the controller's host key with `host_key_fingerprints` (3.1+). The key is checked before
the password is sent, and `ssh_host_key_policy` is then ignored:

```python
client = NetworkHDClientSSH(
    host="192.168.1.100",
    port=10022,
    username="wyrestorm",
    password="networkhd",
    ssh_host_key_policy="reject",  # ignored while fingerprints are pinned
    host_key_fingerprints="SHA256:<base64 from ssh-keygen>",
)
```

Get the fingerprints from a machine you trust on the same network:

```bash
ssh-keyscan -p 10022 192.168.1.100 | ssh-keygen -lf -
```

Controllers typically offer an ECDSA and an RSA key, and paramiko negotiates ECDSA, so pass both lines or at least the
ECDSA one. `host_key_fingerprints` takes one string or a list of strings; each may hold several fingerprints separated
by commas, spaces or newlines, as `SHA256:<base64>` or bare base64, with or without `=` padding. The `ssh-keygen -lf`
output can be pasted as is: everything but the `SHA256:` tokens is ignored. A value with no fingerprint in it raises
`ValueError`; `wyrestorm_networkhd.normalize_fingerprints()` applies the same rules, so you can validate user input with
it.

If the controller presents any other key, `connect()` raises `HostKeyMismatchError` (a `ConnectionError`) carrying the
key it saw in `presented_fingerprint`, and `reconnect()` doesn't retry it.

**Trust on first use.** After every successful connect, `client.host_key_fingerprint` holds the fingerprint of the key
the controller presented, pinned or not (`None` before the first connect). To trust a controller on first use, connect
once without pinning, store `client.host_key_fingerprint`, and pass it as `host_key_fingerprints` from then on. To pin
an existing client without rebuilding it, set `client.host_key_fingerprints = normalize_fingerprints(fp)` (or `None` to
unpin); it's read at every connect, so the next connect or reconnect is checked against it. After a
`HostKeyMismatchError`, update the stored value only if you know why the key changed, for example after the controller
was replaced or reset.

If you can't pin the key, keep the controller's control interface on an isolated network or VLAN, or use RS232.

## 💻 Usage Examples

These assume `api = NHDAPI(client)` inside `async with client:`, as in the [Quick Start](#quick-start). Unlike the Quick
Start, these commands change the state of your system. Device names are the aliases (or hostnames) from your controller.
Each command method returns `True` once the controller acknowledges it and raises an exception otherwise.

### Typed Device Queries

```python
for device in await api.api_query.config_get_device_info():
    print(f"{device.aliasname} ({device.name}), firmware {device.version}")
    if device.cbr_avg_bitrate is not None:  # encoders only
        print(f"  CBR bitrate: {device.cbr_avg_bitrate}")
    if device.audio:  # decoders only
        print(f"  Audio outputs: {[output.name for output in device.audio]}")

for status in await api.api_query.config_get_device_status():
    # NHD-400/600 report "hdcp", NHD-110/200/210 report "hdcp_status"
    print(f"{status.aliasname}: HDCP {status.hdcp or status.hdcp_status}")
```

### Matrix Switching

```python
# Route source1 to two displays
await api.media_stream_matrix_switch.matrix_set("source1", ["display1", "display2"])

# Route video only
await api.media_stream_matrix_switch.matrix_video_set("source2", "display3")
```

### Device Control

```python
# Power displays on through their decoders
await api.connected_device_control.config_set_device_sinkpower("on", ["display1", "display2"])

# Send an infrared code from an encoder
await api.connected_device_control.infrared("0000 0067 0000 0015 0060 0018 0030 0018", "source1")

# Choose an encoder's video input
await api.device_port_switch.config_set_device_videosource("source1", "hdmi")

# Turn a decoder's analog audio up
await api.audio_output.config_set_device_audio_volume_analog("up", "display1")
```

### Video Walls and Multiview

```python
await api.video_wall.scene_active("OfficeVW", "Splitmode")
await api.multiview.mscene_active("display5", "gridlayout")
```

### Text Overlay

```python
color = api.video_stream_text_overlay.get_color_hex("white", "nhd110_140")
await api.video_stream_text_overlay.config_set_device_osd_param(
    text="Hello World", position_x=100, position_y=100, text_color=color, text_size=2, tx="source1"
)
await api.video_stream_text_overlay.config_set_device_osd("on", "source1")
```

## 🔔 Notifications

Register callbacks with `client.register_notification_callback(type, callback)`, before or after connecting. The types
are `"endpoint"`, `"cecinfo"`, `"irinfo"`, `"serialinfo"`, `"video"` and `"sink"`; each callback receives the parsed
notification model (see [Models](reference/models.md)). Coroutine callbacks are scheduled as tasks. Exceptions raised by
callbacks are logged and don't affect the connection. Multi-line `serialinfo` and `irinfo` notifications are assembled
before your callback sees them. A `serialinfo` is framed by its stated length, which is trusted: a length over 65536 is
dropped with a warning, and `hex` data containing anything but hex digits and whitespace stops the framing so the
following lines are read normally. Any line or `irinfo` over 64 KiB is dropped with a warning in the log.

CEC notifications from NHD-400/500 endpoints can be switched on or off:

```python
await api.api_notifications.config_set_device_cec_notify("on", "ALL_RX")
```

## 🪵 Logging

The library logs to the `wyrestorm_networkhd` logger and doesn't configure logging itself. Configure it in your
application, or for a quick script call the helper, which sets up the `wyrestorm_networkhd` logger only:

```python
from wyrestorm_networkhd.logging_config import setup_logging

setup_logging(level="DEBUG")  # also accepts log_file=Path("networkhd.log")
```

At DEBUG level the library logs every command and raw response, which is the most useful thing to attach to a bug
report.
