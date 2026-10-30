# 🔧 Troubleshooting

## 🚀 Quick Diagnostics

Run this first. It turns on debug logging, connects, and sends one read-only command:

```python
import asyncio

from wyrestorm_networkhd import NetworkHDClientSSH
from wyrestorm_networkhd.logging_config import setup_logging


async def test_connection():
    setup_logging(level="DEBUG")
    client = NetworkHDClientSSH(
        host="192.168.1.100",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn",
        timeout=10.0,
    )
    async with client:
        print(await client.send_command("config get version"))


asyncio.run(test_connection())
```

## 🔌 Connection Issues

### `ConnectionError: Connection failed: ...` or a connect timeout

1. Check the controller is reachable: `ping 192.168.1.100`.
2. Check SSH is enabled. The controller ships with only Telnet (port 23) enabled, and this library doesn't support
   Telnet. Enable SSH in the controller's web interface; it listens on port **10022**, not 22.
3. Check you're using the controller's address. The library talks to the NHD-000-CTL / NHD-CTL-PRO, not to encoders or
   decoders.
4. On a slow network, raise the connect timeout: `NetworkHDClientSSH(..., timeout=30.0)`.

### `AuthenticationError: Authentication failed for user ...`

The controller rejected the username or password. The defaults are `wyrestorm` / `networkhd`; check whether yours were
changed. `reconnect()` doesn't retry this error.

### `ConnectionError: SSH error: Server '...' not found in known_hosts`

You used `ssh_host_key_policy="reject"`. The library doesn't load a `known_hosts` file, so `"reject"` refuses every
controller. Pin the controller's key with `host_key_fingerprints`, or use `"warn"` or `"auto_add"`, both of which accept
any host key; see [SSH Host Keys](index.md#ssh-host-keys).

### `HostKeyMismatchError: SSH host key of '...' is SHA256:..., which does not match ...`

You pinned `host_key_fingerprints` and the controller presented a different key, so the connection was closed before the
password was sent; `reconnect()` doesn't retry. Either the controller was replaced or reset (its key changes), or
something on the network is impersonating it. Check the key from a machine you trust with
`ssh-keyscan -p 10022 <host> | ssh-keygen -lf -`, and update the pin to the new value (also in
`e.presented_fingerprint`) only if you know why it changed. See [SSH Host Keys](index.md#ssh-host-keys).

### `ValueError: No SHA256 host key fingerprint found`

`host_key_fingerprints` held nothing that looks like a SHA256 fingerprint (43 base64 characters, optionally after
`SHA256:`). MD5 fingerprints (`MD5:aa:bb:...`) aren't accepted. Paste the output of
`ssh-keyscan -p 10022 <host> | ssh-keygen -lf -`.

### `ValueError: Invalid ssh_host_key_policy`

The policy must be `"auto_add"`, `"reject"` or `"warn"`.

### `ConnectionLostError: Connection to '...' was lost`

The link dropped (network outage, controller reboot), or `disconnect()`/`connect()` was called while the command was
waiting. `is_connected()` is now `False`. Call `await client.reconnect()`; see [Reconnecting](index.md#reconnecting).

Over RS232 a failed write marks the link as lost, but a cable pulled without an error shows up only as commands raising
`TimeoutError`.

### RS232: the port won't open

1. Install the extra: `pip install "wyrestorm-networkhd[rs232]"`. Without it, using `NetworkHDClientRS232` raises
   `ImportError`.
2. Check the port name (`/dev/ttyUSB0`, `/dev/tty.usbserial-*` on macOS, `COM3` on Windows) and that your user may open
   it. On Linux that usually means being in the `dialout` group:
   ```bash
   sudo usermod -a -G dialout $USER  # then log out and back in
   ```
3. The controller's RS232 port runs at 9600 baud, 8 data bits, no parity, 1 stop bit: use `baudrate=9600`.
4. `ValueError: Unknown serial options` means you passed a keyword argument that isn't an async-pyserial
   `SerialPortOptions` attribute.

## ⏱️ Command Issues

### `TimeoutError: Operation '...' timed out after 10.0s`

The reply didn't finish within `response_timeout`: nothing came back, or lines were still arriving when it expired (a
reply is never returned cut short at the deadline). Check the connection, then try a longer timeout for that command:

```python
response = await client.send_command("config get devicejsonstring", response_timeout=20.0)
```

### A reply is cut short

A reply ends when no line arrives for `response_line_timeout` (0.3 s by default). If a large multi-line reply is
truncated, raise it: `send_command(..., response_line_timeout=1.0)`.

### `UnknownCommandError: Unknown command: ...`

The controller answered `unknown command`: the command or its parameters are wrong, or your firmware doesn't support it.
Check the command against the API document on the [Resources](resources.md) page and the "Command applies to" list in
the method's docstring.

### `CommandError`

Either the controller answered `ERROR ...` (the message includes its reply), or the command contained a line break.
Commands must be a single line.

### `DeviceQueryError` or `DeviceNotFoundError`

The device name you passed is unknown or the device returned an error (for example it is offline). Names are the aliases
or hostnames from `api.api_query.config_get_devicelist()`. When you query all devices, entries with errors are skipped
instead of raising, even if there is only one device.

### `ResponseError`

The reply couldn't be parsed into a model, or a command wasn't acknowledged as expected. Turn on debug logging and open
an issue with the raw response from the log.

## 📡 Notification Issues

### Callbacks never fire

1. Check the type: `"endpoint"`, `"cecinfo"`, `"irinfo"`, `"serialinfo"`, `"video"` or `"sink"`.
2. Keep the connection open. Notifications are only received while connected.
3. CEC notifications from NHD-400/500 endpoints can be switched off on the controller. Switch them on with
   `await api.api_notifications.config_set_device_cec_notify("on", "ALL_DEV")` (or `"ALL_TX"`, `"ALL_RX"`, or device
   names).

### A callback raised an exception

Exceptions from callbacks are logged by the `wyrestorm_networkhd` logger and don't stop other callbacks or the
connection. Turn on logging to see them. Notifications that can't be parsed are logged as warnings and skipped.

## 🚨 Exceptions

Everything below is importable from `wyrestorm_networkhd` and subclasses `NetworkHDError`.

| Exception              | Also a                     | Raised when                                                      |
| ---------------------- | -------------------------- | ---------------------------------------------------------------- |
| `ConnectionError`      | `builtins.ConnectionError` | Connecting fails, or a command is sent while not connected       |
| `ConnectionLostError`  | `ConnectionError`          | A command is sent, or was waiting, after the link dropped        |
| `ReconnectionError`    | `ConnectionError`          | Every `reconnect()` attempt failed (`attempts`, `last_error`)    |
| `HostKeyMismatchError` | `ConnectionError`          | The SSH host key matched none of `host_key_fingerprints`         |
| `AuthenticationError`  |                            | The controller rejected the SSH credentials                      |
| `TimeoutError`         | `builtins.TimeoutError`    | The reply didn't finish within `response_timeout`                |
| `CommandError`         |                            | The controller answered `ERROR`, or the command contained CR/LF  |
| `UnknownCommandError`  | `CommandError`             | The controller answered `unknown command`                        |
| `ResponseError`        | `ValueError`               | A reply couldn't be parsed or wasn't the expected acknowledgment |
| `DeviceQueryError`     |                            | A query for a named device returned an error entry for it        |
| `DeviceNotFoundError`  |                            | `config_get_name()` was asked for a device that doesn't exist    |

## 📞 Getting Help

[Open an issue](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/issues/new/choose) and include:

- Controller model and the output of `config get version` (firmware and API version)
- Connection type (SSH or RS232) and the library version (`wyrestorm_networkhd.__version__`)
- The code that fails and the full traceback
- A debug log from `setup_logging(level="DEBUG")`, with passwords and addresses removed
