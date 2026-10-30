# WyreStorm NetworkHD Python Client

[![PyPI version](https://badge.fury.io/py/wyrestorm-networkhd.svg)](https://badge.fury.io/py/wyrestorm-networkhd)
[![Python Support](https://img.shields.io/pypi/pyversions/wyrestorm-networkhd.svg)](https://pypi.org/project/wyrestorm-networkhd/)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Matt-Hadley/8f4a6e65e2d520f63a82a34cddcc4b56/raw/coverage.json)](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An async Python client for WyreStorm NetworkHD AV-over-IP systems. It talks to the NetworkHD controller over SSH or
RS232, wraps the NetworkHD API in typed methods and response models, and delivers real-time notifications to your
callbacks.

📖 **[Documentation](https://matt-hadley.github.io/wyrestorm-networkhd-py/)** | 🔄
**[Migrating from 2.x](https://matt-hadley.github.io/wyrestorm-networkhd-py/migration/)** | 💻
**[API Reference](https://matt-hadley.github.io/wyrestorm-networkhd-py/reference/core/)** | 🔧
**[Troubleshooting](https://matt-hadley.github.io/wyrestorm-networkhd-py/troubleshooting/)**

## Supported hardware

- **Controllers:** NHD-000-CTL and NHD-CTL-PRO, as covered by the
  [NetworkHD API v6.7](https://matt-hadley.github.io/wyrestorm-networkhd-py/resources/) document. The library talks to
  the controller only, never to endpoints directly.
- **Endpoints:** the 100, 200, 400, 500 and 600 series encoders and decoders that the API document covers. Some commands
  apply to certain series only; each method's docstring lists them.
- **Tested on:** NHD-000-CTL firmware v9.4.7 (API v1.28) with NHD-400 TX/RX firmware v2.5.6, over SSH.
- **Connection:** SSH (port 10022) or RS232. The controller ships with only Telnet enabled, which this library does not
  support: enable SSH in the controller's web interface first.

## Installation

```bash
pip install wyrestorm-networkhd

# With RS232 support
pip install "wyrestorm-networkhd[rs232]"
```

Requires Python 3.11 or later.

## Quick Start

```python
import asyncio

from wyrestorm_networkhd import NHDAPI, NetworkHDClientSSH


async def main():
    client = NetworkHDClientSSH(
        host="192.168.1.100",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn",
    )

    async with client:
        api = NHDAPI(client)

        print(await api.api_query.config_get_version())

        for device in await api.api_query.config_get_devicejsonstring():
            print(f"{device.aliasName} ({device.deviceType}): {'online' if device.online else 'offline'}")


asyncio.run(main())
```

This only reads from the controller. The [documentation](https://matt-hadley.github.io/wyrestorm-networkhd-py/) covers
switching, video walls, multiview, notifications, RS232 and the SSH host key policies (`"warn"` accepts any host key).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
