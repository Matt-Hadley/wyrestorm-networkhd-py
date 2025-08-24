# 🌊 WyreStorm NetworkHD Python Client

[![PyPI version](https://badge.fury.io/py/wyrestorm-networkhd.svg)](https://badge.fury.io/py/wyrestorm-networkhd)
[![Python Support](https://img.shields.io/pypi/pyversions/wyrestorm-networkhd.svg)](https://pypi.org/project/wyrestorm-networkhd/)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Matt-Hadley/8f4a6e65e2d520f63a82a34cddcc4b56/raw/coverage.json)](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python client library for WyreStorm NetworkHD devices, providing a high-level interface for device control and
monitoring. Features **strongly typed APIs**, **async/await support**, **multiple connection types** (SSH and RS232),
**comprehensive API coverage**, **robust error handling**, and **real-time notifications**.

## 📦 Installation

```bash
pip install wyrestorm-networkhd
```

## 🚀 Quick Start

### SSH Connection

```python
from wyrestorm_networkhd import NetworkHDClientSSH, NHDAPI

# Create client with SSH connection
client = NetworkHDClientSSH(
    host="192.168.1.100",
    port=10022,
    username="wyrestorm",
    password="networkhd",
    ssh_host_key_policy="warn"
    # Optional configuration parameters for reliability and performance:
    # circuit_breaker_timeout=30.0,        # Time before auto-reset after connection failures
    # heartbeat_interval=30.0,             # Interval for connection health monitoring
    # message_dispatcher_interval=0.1      # Polling frequency for incoming messages
)
```

### RS232 Connection (Optional)

```python
from wyrestorm_networkhd import NetworkHDClientRS232, NHDAPI

# Install RS232 support: pip install wyrestorm-networkhd[rs232]
client = NetworkHDClientRS232(
    port="/dev/ttyUSB0",  # Linux: /dev/ttyUSB0, Windows: COM1
    baudrate=115200,
    timeout=10.0
    # Optional configuration parameters for reliability and performance:
    # circuit_breaker_timeout=30.0,        # Time before auto-reset after connection failures
    # heartbeat_interval=30.0,             # Interval for connection health monitoring
    # message_dispatcher_interval=0.05     # Polling frequency for incoming messages (faster for RS232)
)
```

### Basic Usage

```python
async def main():
    # Create client (SSH or RS232)
    client = NetworkHDClientSSH(
        host="192.168.1.100",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn"
    )

    # Use async context manager for automatic connection handling
    async with client:
        # Create API wrapper for organized command access
        api = NHDAPI(client)

        # Execute commands and get typed responses
        device_list = await api.api_query.get_devicelist()
        matrix_info = await api.api_query.matrix_get()
        await api.video_wall.scene_active("office", "splitmode")

# Run the async function
import asyncio
asyncio.run(main())
```

## 📋 API Categories

API categories match those in the [API Reference](reference/).

- **System Configuration**: Version info, IP settings, device lists
- **Device Configuration**: Device names, info, and status
- **Matrix Switching**: Video, audio, USB, infrared, and serial routing
- **Video Walls**: Scene management and logical screen control
- **Multiview**: Preset and custom layout management
- **Device Control**: Reboot, reset, and port switching
- **Notifications**: Real-time device status updates

## 🔗 Connection Types

### SSH Connection

The SSH client requires explicit SSH host key verification policy selection to ensure users make conscious security
decisions.

### RS232 Connection

The RS232 client provides serial communication support as an optional extension. Install with:

```bash
pip install wyrestorm-networkhd[rs232]
```

**Note**: RS232 support requires the `async-pyserial` package and appropriate serial port permissions on your system.

### Connection Configuration

Both connection types support optional configuration parameters for reliability and performance tuning:

- **`circuit_breaker_timeout`** (default: 30.0 seconds): Time after which the circuit breaker automatically resets
  following connection failures. The circuit breaker prevents cascading failures by temporarily blocking connection
  attempts after 3 consecutive failures.

- **`heartbeat_interval`** (default: 30.0 seconds): Interval for connection health monitoring and metrics tracking. Used
  internally for connection state management.

- **`message_dispatcher_interval`** (default: 0.1s SSH, 0.05s RS232): Polling frequency for processing incoming
  messages. Lower values provide faster response times but use more CPU. RS232 defaults to a faster interval due to its
  typically higher message throughput.

### Security Recommendations

SSH Client:

- **Production Environments**: Use `"reject"` or `"warn"` policies
- **Development/Testing**: Use `"auto_add"` policy
- **Controlled Networks**: `"auto_add"` may be acceptable if network security is assured Logging:
- **Monitor Logs**: Always monitor logs for security warnings when using permissive policies

## 💻 Usage Examples

The following examples assume you have a client connected as shown in the [Basic Usage](#basic-usage) section above. All
code snippets should be placed inside the `async with client:` block.

### Matrix Switching Examples

```python
# Assign source1 to multiple displays
response = await api.media_stream_matrix_switch.matrix_set("source1", ["display1", "display2"])

# Set video-only routing
response = await api.media_stream_matrix_switch.matrix_video_set("source2", "display3")

# Get current matrix status
matrix_status = await api.api_query.matrix_get()
```

### Device Control Examples

```python
# Send power on command to displays
response = await api.connected_device_control.config_set_device_sinkpower("on", ["display1", "display2"])

# Send custom infrared command
ir_data = "0000 0067 0000 0015 0060 0018 0030 0018"
response = await api.connected_device_control.infrared(ir_data, "source1")

# Switch video source on encoder
response = await api.device_port_switch.config_set_device_videosource("source1", "hdmi")

# Control analog audio volume
response = await api.audio_output.config_set_device_audio_volume_analog("up", "display1")
```

### Video Wall and Multiview Examples

```python
# Apply a video wall scene
response = await api.video_wall.scene_active("OfficeVW", "Splitmode")

# Apply multiview layout
response = await api.multiview.mscene_active("display5", "gridlayout")
```

### Text Overlay Examples

```python
# Configure text overlay
color = api.video_stream_text_overlay.get_color_hex("white", "nhd110_140")
response = await api.video_stream_text_overlay.config_set_device_osd_param(
    text="Hello World",
    position_x=100,
    position_y=100,
    text_color=color,
    text_size=2,
    tx="source1"
)

# Enable text overlay
response = await api.video_stream_text_overlay.config_set_device_osd("on", "source1")
```

## 🔔 Real-time Notifications

The client includes built-in support for real-time device notifications:

```python
from wyrestorm_networkhd import NetworkHDClientSSH

client = NetworkHDClientSSH(
    host="192.168.1.100",
    port=10022,
    username="admin",
    password="secret",
    ssh_host_key_policy="warn"
)

# Register notification callbacks
def on_device_status(notification):
    print(f"Device {notification.device} is {'online' if notification.online else 'offline'}")

def on_cec_data(notification):
    print(f"CEC data from {notification.device}: {notification.cec_data}")

# Register callbacks for different notification types
client.register_notification_callback("endpoint", on_device_status)
client.register_notification_callback("cecinfo", on_cec_data)

# Connect and start receiving notifications
await client.connect()
# Notifications will be automatically handled while connected
```
