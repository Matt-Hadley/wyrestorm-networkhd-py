# Migrating from 2.x to 3.0

3.0 reworks the transport, error handling and logging. Command methods on `NHDAPI` keep their names, arguments and
return types, so most code only needs the changes below if it caught exceptions, read empty responses, tuned the client
or relied on the library configuring logging.

## Client constructor

`circuit_breaker_timeout` and `heartbeat_interval` are still accepted, but they do nothing and emit a
`DeprecationWarning`. They will be removed in 4.0. The circuit breaker is gone, and the heartbeat is replaced by SSH
keepalive packets every 30 seconds.

```python
# 2.x
client = NetworkHDClientSSH(
    host="192.168.1.100",
    port=10022,
    username="wyrestorm",
    password="networkhd",
    ssh_host_key_policy="warn",
    circuit_breaker_timeout=30.0,
    heartbeat_interval=30.0,
)

# 3.0
client = NetworkHDClientSSH(
    host="192.168.1.100",
    port=10022,
    username="wyrestorm",
    password="networkhd",
    ssh_host_key_policy="warn",
)
```

## Command timing

Paramiko's blocking calls now run off the event loop, responses are framed by the command echo, and the default
`response_line_timeout` of `send_command()` dropped from 1.0 s to 0.3 s. A command takes about 0.5 s on real hardware,
down from at least 1 s. If a device sends a slow multi-line reply, raise `response_line_timeout` for that call:

```python
response = await client.send_command("config get devicejsonstring", response_line_timeout=1.0)
```

## Errors from `send_command()`

`send_command()`, and every `NHDAPI` method that uses it, now raises instead of returning odd strings:

| Situation                             | 2.x                                  | 3.0                                     |
| ------------------------------------- | ------------------------------------ | --------------------------------------- |
| No reply within `response_timeout`    | returned `""`                        | raises `TimeoutError`                   |
| Device answers `unknown command`      | returned the text                    | raises `UnknownCommandError`            |
| Device answers `ERROR...`             | raised `CommandError`                | raises `CommandError` (unchanged)       |
| Command contains CR or LF             | sent as is                           | raises `CommandError`, nothing is sent  |
| The link has dropped                  | varied                               | raises `ConnectionLostError`            |
| Response can't be parsed into a model | `ValueError`, `TypeError` or similar | raises `ResponseError` (a `ValueError`) |

```python
# 2.x
response = await client.send_command("config get version")
if not response:
    print("no reply")

# 3.0
from wyrestorm_networkhd import TimeoutError, UnknownCommandError

try:
    response = await client.send_command("config get version")
except TimeoutError:
    print("no reply")
except UnknownCommandError:
    print("the controller didn't understand the command")
```

## Exceptions

All exceptions are exported from the package (in 2.x you imported them from `wyrestorm_networkhd.exceptions`, which
still works):

```python
from wyrestorm_networkhd import CommandError, ConnectionError, NetworkHDError, ResponseError
```

They also subclass the matching builtins, so generic handlers catch them:

- `ConnectionError` (and `ConnectionLostError`, `ReconnectionError`) subclass `builtins.ConnectionError`.
- `TimeoutError` subclasses `builtins.TimeoutError`.
- `ResponseError` subclasses `ValueError`.

Note that `from wyrestorm_networkhd import ConnectionError, TimeoutError` shadows the builtins in your module. Import
the module instead if you need both.

## Reconnecting

`reconnect()` now has defaults, `max_attempts=5` and `delay=1.0`, and backs off exponentially (capped at 30 s, with
jitter). When every attempt fails it raises `ReconnectionError` (a `ConnectionError`) instead of a plain
`ConnectionError`. A rejected login raises `AuthenticationError` straight away and is not retried.

After the link drops, `is_connected()` returns `False` and `send_command()` raises `ConnectionLostError` until you
reconnect:

```python
# 2.x
await client.reconnect(max_attempts=5, delay=1.0)

# 3.0
from wyrestorm_networkhd import AuthenticationError, ConnectionLostError, ReconnectionError

try:
    matrix = await api.api_query.matrix_get()
except ConnectionLostError:
    try:
        await client.reconnect()
    except AuthenticationError:
        raise  # wrong credentials: retrying won't help
    except ReconnectionError as e:
        print(f"gave up after {e.attempts} attempts: {e.last_error}")
```

## Logging

Importing the package no longer configures logging. On import, 2.x replaced the root logger's handlers with an INFO
console handler and set the `paramiko` and `asyncio` loggers to WARNING; 3.0 only adds a `NullHandler` to the
`wyrestorm_networkhd` logger. Configure logging in your application as usual, or call the opt-in helper, which
configures the `wyrestorm_networkhd` logger only:

```python
from wyrestorm_networkhd.logging_config import setup_logging

setup_logging(level="DEBUG")
```

## Notification callbacks

Callbacks may now be coroutine functions; they are scheduled as tasks and their exceptions are logged. Multi-line
`serialinfo` and `irinfo` notifications are assembled before your callback sees them, so `serial_data` and `ir_data`
hold the whole payload.

```python
async def on_serial(notification):
    await store(notification.device, notification.serial_data)

client.register_notification_callback("serialinfo", on_serial)
```

## Query parsing

- Unknown JSON fields in device replies are ignored instead of failing the parse.
- Real JSON booleans and empty values are accepted.
- `config_get_device_info()` and `config_get_device_status()` without a device skip per-device error entries (for
  example an offline endpoint) and return the rest. Querying a single device that returns an error still raises
  `DeviceQueryError`.

## RS232 client

The RS232 client now uses async-pyserial's real API (`SerialPortOptions`):

- `timeout` is the write timeout in seconds.
- Extra keyword arguments must be `SerialPortOptions` attributes (`bytesize`, `stopbits`, `parity`, `read_timeout`,
  `write_timeout`, `read_bufsize`); anything else raises `ValueError`.
- `NetworkHDClientRS232` is imported lazily, so `import wyrestorm_networkhd` works without the `rs232` extra. Install it
  with `pip install "wyrestorm-networkhd[rs232]"` before using the class.

```python
from wyrestorm_networkhd import NetworkHDClientRS232

client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600, timeout=5.0, stopbits=1)
```

## Typing

The package ships `py.typed`, so mypy and pyright use its type hints. `NHDAPI` now declares its command groups as
ordinary attributes (same names as before: `api_query`, `video_wall` and so on), so IDEs can complete them.
