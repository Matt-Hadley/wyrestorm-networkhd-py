# WyreStorm NetworkHD Python Client

[![PyPI version](https://badge.fury.io/py/wyrestorm-networkhd.svg)](https://badge.fury.io/py/wyrestorm-networkhd)
[![Python Support](https://img.shields.io/pypi/pyversions/wyrestorm-networkhd.svg)](https://pypi.org/project/wyrestorm-networkhd/)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Matt-Hadley/8f4a6e65e2d520f63a82a34cddcc4b56/raw/coverage.json)](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python client library for WyreStorm NetworkHD devices, providing a high-level interface for device control and
monitoring. Features **strongly typed APIs**, **async/await support**, **multiple connection types** (SSH and RS232),
**comprehensive API coverage**, **robust error handling**, and **real-time notifications**.

📖 **[View Documentation](https://matt-hadley.github.io/wyrestorm-networkhd-py/)** | 🚀 **[Quick Start](#quick-start)**
| 💻 **[API Reference](https://matt-hadley.github.io/wyrestorm-networkhd-py/reference/core/)** | 🔧
**[Troubleshooting](https://matt-hadley.github.io/wyrestorm-networkhd-py/troubleshooting/)**

## Installation

```bash
pip install wyrestorm-networkhd

# For RS232 support (optional)
pip install wyrestorm-networkhd[rs232]
```

## Quick Start

```python
import asyncio
from wyrestorm_networkhd import NetworkHDClientSSH, NHDAPI

async def main():
    # Create SSH client
    client = NetworkHDClientSSH(
        host="192.168.1.100",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn"
    )

    # Register notification callbacks for real-time updates
    def on_device_status(notification):
        print(f"Device {notification.device} is {'online' if notification.online else 'offline'}")

    def on_cec_data(notification):
        print(f"CEC data from {notification.device}: {notification.cec_data}")

    client.register_notification_callback("endpoint", on_device_status)
    client.register_notification_callback("cecinfo", on_cec_data)

    # Use async context manager for automatic connection handling
    async with client:
        # Create API wrapper for organized command access
        api = NHDAPI(client)

        # Execute commands and get typed responses
        device_list = await api.api_query.config_get_devicelist()
        matrix_info = await api.api_query.matrix_get()

        # Query device information with typed responses
        devices = await api.api_query.config_get_device_info()
        for device in devices:
            print(f"Device {device.aliasname} ({device.name}) - IP: {device.ip4addr}")

        # Query device status with typed responses
        status_list = await api.api_query.config_get_device_status()
        for status in status_list:
            print(f"Device {status.aliasname} - HDMI out: {status.hdmi_out_active}")
        await api.video_wall.scene_active("office", "splitmode")

        # Real-time notifications are automatically handled in the background

# Run the async function
asyncio.run(main())
```

## 📚 Documentation

**🌐 [Complete Documentation](https://matt-hadley.github.io/wyrestorm-networkhd-py/)**

- **[Getting Started](https://matt-hadley.github.io/wyrestorm-networkhd-py/)**: Installation, configuration, and usage
  examples
- **[API Reference](https://matt-hadley.github.io/wyrestorm-networkhd-py/reference/core/)**: Complete API documentation
  with type hints
- **[Core Components](https://matt-hadley.github.io/wyrestorm-networkhd-py/reference/core/)**: Client classes and
  connection management
- **[Commands](https://matt-hadley.github.io/wyrestorm-networkhd-py/reference/commands/)**: All command modules and
  methods
- **[Models](https://matt-hadley.github.io/wyrestorm-networkhd-py/reference/models/)**: Data models and response
  structures
- **[Resources](https://matt-hadley.github.io/wyrestorm-networkhd-py/resources/)**: NetworkHD raw API documentation
- **[Troubleshooting](https://matt-hadley.github.io/wyrestorm-networkhd-py/troubleshooting/)**: Common issues and
  solutions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
