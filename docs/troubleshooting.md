# 🔧 Troubleshooting

This guide helps you resolve common issues when using the WyreStorm NetworkHD Python client library.

## 🚀 Quick Diagnostics

### Check Your Setup

```python
import asyncio
from wyrestorm_networkhd import NetworkHDClientSSH

async def test_connection():
    client = NetworkHDClientSSH(
        host="your_device_ip",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn",
        timeout=10.0
    )

    try:
        await client.connect()
        print("✅ Connection successful!")
        response = await client.send_command("config get version")
        print(f"Device version: {response}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

# Run the test
asyncio.run(test_connection())
```

## 🔌 Connection Issues

### SSH Connection Problems

#### Problem: `ConnectionRefusedError` or `TimeoutError`

**Symptoms:**

```
ConnectionRefusedError: [Errno 61] Connection refused
# or
asyncio.TimeoutError: Timeout connecting to device
```

**Solutions:**

1. **Verify network connectivity:**

   ```bash
   ping your_device_ip
   telnet your_device_ip 10022
   ```

2. **Check SSH service status on device:**
   - Ensure SSH is enabled in NetworkHD web interface
   - Verify SSH port (usually 10022, not 22)
   - Check firewall rules

3. **Adjust timeout settings:**
   ```python
   client = NetworkHDClientSSH(
       host="192.168.1.100",
       port=10022,
       username="wyrestorm",
       password="networkhd",
       ssh_host_key_policy="warn",
       timeout=30.0,  # Increase timeout
       response_timeout=15.0  # Command response timeout
   )
   ```

#### Problem: `AuthenticationException`

**Symptoms:**

```
paramiko.ssh_exception.AuthenticationException: Authentication failed
```

**Solutions:**

1. **Verify credentials:**

   ```python
   # Default credentials for most devices
   username="wyrestorm"
   password="networkhd"
   ```

2. **Check for custom credentials:**
   - Some devices may have changed default passwords
   - Try logging in via web interface first
   - Contact your network administrator

#### Problem: `SSHException` - Host key verification failed

**Symptoms:**

```
paramiko.ssh_exception.SSHException: Server host key verification failed
```

**Solutions:**

1. **Use auto_add policy (less secure):**

   ```python
   ssh_host_key_policy="auto_add"
   ```

2. **Use warn policy (recommended):**

   ```python
   ssh_host_key_policy="warn"  # Shows warning but continues
   ```

3. **For production, use strict policy with known_hosts:**
   ```python
   ssh_host_key_policy="strict"  # Requires proper host key management
   ```

### RS232 Connection Problems

#### Problem: `SerialException` or device not found

**Symptoms:**

```
serial.serialutil.SerialException: could not open port /dev/ttyUSB0
```

**Solutions:**

1. **Install RS232 dependencies:**

   ```bash
   pip install wyrestorm-networkhd[rs232]
   ```

2. **Check device permissions (Linux/macOS):**

   ```bash
   # Add user to dialout group
   sudo usermod -a -G dialout $USER
   # Log out and back in

   # Check port permissions
   ls -l /dev/ttyUSB0
   # or
   ls -l /dev/tty.usbserial-*
   ```

3. **Find correct serial port:**

   ```python
   import serial.tools.list_ports

   # List available ports
   ports = serial.tools.list_ports.comports()
   for port in ports:
       print(f"Port: {port.device}, Description: {port.description}")
   ```

4. **Adjust serial settings:**

   ```python
   from wyrestorm_networkhd import NetworkHDClientRS232

   client = NetworkHDClientRS232(
       port="/dev/ttyUSB0",  # or "COM3" on Windows
       baudrate=115200,      # Try different rates: 9600, 19200, 38400
       timeout=10.0,
       response_timeout=5.0
   )
   ```

## ⚡ Performance Issues

### Slow Response Times

#### Problem: Commands taking too long to execute

**Solutions:**

1. **Optimize timeout settings:**

   ```python
   client = NetworkHDClientSSH(
       host="192.168.1.100",
       port=10022,
       username="wyrestorm",
       password="networkhd",
       ssh_host_key_policy="warn",
       timeout=5.0,          # Connection timeout
       response_timeout=3.0  # Command response timeout
   )
   ```

2. **Use concurrent execution for multiple commands:**

   ```python
   import asyncio
   from wyrestorm_networkhd import NHDAPI, NetworkHDClientSSH

   async def run_multiple_commands():
       client = NetworkHDClientSSH(...)

       async with client:
           api = NHDAPI(client)

           # Run commands concurrently
           tasks = [
               api.api_query.config_get_devicelist(),
               api.api_query.matrix_get(),
               api.api_query.config_get_version()
           ]

           results = await asyncio.gather(*tasks, return_exceptions=True)
           return results
   ```

3. **Check network latency:**
   ```bash
   ping -c 10 your_device_ip
   ```

### Memory Usage Issues

#### Problem: High memory consumption with notifications

**Solutions:**

1. **Limit notification callbacks:**

   ```python
   # Only register for needed notification types
   client.register_notification_callback("endpoint", callback)
   # Don't register for all types if not needed
   ```

2. **Use weak references for callbacks:**

   ```python
   import weakref

   def create_callback(obj):
       obj_ref = weakref.ref(obj)

       def callback(notification):
           obj = obj_ref()
           if obj is not None:
               obj.handle_notification(notification)

       return callback
   ```

## 📡 Notification Issues

### Not Receiving Notifications

#### Problem: Notification callbacks not firing

**Solutions:**

1. **Verify notification registration:**

   ```python
   def device_callback(notification):
       print(f"Device notification: {notification}")

   # Register before connecting
   client.register_notification_callback("endpoint", device_callback)

   async with client:
       # Notifications should now be received
       await asyncio.sleep(10)  # Wait for notifications
   ```

2. **Enable notifications on device:**

   ```python
   api = NHDAPI(client)

   # Enable specific notifications
   await api.api_notifications.config_set_device_endpoint_notify("on", "all")
   await api.api_notifications.config_set_device_cec_notify("on", "all")
   ```

3. **Check notification types:**
   ```python
   # Available notification types:
   # "endpoint" - Device online/offline status
   # "cecinfo" - CEC data
   # "video" - Video input changes
   # "sink" - Sink power status
   # "irinfo" - Infrared data
   # "serialinfo" - RS232 data
   ```

### Notification Parsing Errors

#### Problem: Notifications causing parsing exceptions

**Solutions:**

1. **Enable debug logging:**

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger("wyrestorm_networkhd")
   logger.setLevel(logging.DEBUG)
   ```

2. **Add error handling in callbacks:**

   ```python
   def safe_callback(notification):
       try:
           # Your notification handling code
           print(f"Received: {notification}")
       except Exception as e:
           print(f"Callback error: {e}")
           # Log the raw notification for debugging
           print(f"Raw notification: {repr(notification)}")

   client.register_notification_callback("endpoint", safe_callback)
   ```

## 🏗️ Development Issues

### Import Errors

#### Problem: Module not found errors

**Solutions:**

1. **Install in development mode:**

   ```bash
   pip install -e .
   # or with optional dependencies
   pip install -e ".[rs232,dev]"
   ```

2. **Check Python path:**

   ```python
   import sys
   print(sys.path)

   # Add project root if needed
   import os
   sys.path.insert(0, os.path.dirname(__file__))
   ```

### Type Checking Issues

#### Problem: MyPy or IDE type errors

**Solutions:**

1. **Install type stubs:**

   ```bash
   pip install types-paramiko types-pyserial
   ```

2. **Check py.typed file exists:**
   ```python
   import wyrestorm_networkhd
   print(wyrestorm_networkhd.__file__)  # Should show py.typed in same directory
   ```

## 🛠️ Device-Specific Issues

### WyreStorm NetworkHD 110/140 Series

#### Problem: Commands not recognized

**Solutions:**

1. **Check firmware version:**

   ```python
   version = await api.api_query.config_get_version()
   print(f"Firmware: {version}")
   ```

2. **Use device-specific command variants:**
   ```python
   # Different device models may return different field sets
   try:
       # Query device info and handle different device types
       devices = await api.api_query.config_get_device_info()
       for device in devices:
           # Handle NHD-400 vs NHD-600 series differences
           if device.hdcp:  # NHD-400/600 series
               print(f"Device {device.aliasname}: HDCP={device.hdcp}")
           elif device.hdcp_status:  # NHD-110/200 series
               print(f"Device {device.aliasname}: HDCP Status={device.hdcp_status}")
   except Exception as e:
       print(f"Device query failed: {e}")
   ```

### Network Configuration Issues

#### Problem: Device not responding after network changes

**Solutions:**

1. **Reset network settings via serial console**
2. **Check IP configuration:**

   ```python
   ip_settings = await api.api_query.config_get_ipsetting()
   print(f"IP settings: {ip_settings}")
   ```

3. **Use device discovery if available:**
   ```bash
   # Use manufacturer's discovery tool first
   # Then connect using discovered IP
   ```

## 📞 Getting Help

### Enable Detailed Logging

```python
import logging

# Enable debug logging for the library
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable paramiko debug logging for SSH issues
logging.getLogger("paramiko").setLevel(logging.DEBUG)
```

### Collect Diagnostic Information

```python
import platform
import sys
import wyrestorm_networkhd

print("System Information:")
print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Library version: {wyrestorm_networkhd.__version__}")

# Test basic connectivity
# ... run your failing code with debug logging enabled
```

### Report Issues

If you encounter a bug or need help:

1. **Check existing issues:** [GitHub Issues](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/issues)
2. **Provide detailed information:**
   - Python version and platform
   - Library version
   - Complete error traceback
   - Code that reproduces the issue
   - Device model and firmware version
3. **Enable debug logging** and include relevant log output

### Community Support

- **Documentation:**
  [https://matt-hadley.github.io/wyrestorm-networkhd-py/](https://matt-hadley.github.io/wyrestorm-networkhd-py/)
- **Source Code:**
  [https://github.com/Matt-Hadley/wyrestorm-networkhd-py](https://github.com/Matt-Hadley/wyrestorm-networkhd-py)
- **Issues:** [GitHub Issues](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/issues)

## 🚨 Common Error Codes

| Error                     | Likely Cause                    | Solution                                |
| ------------------------- | ------------------------------- | --------------------------------------- |
| `ConnectionRefusedError`  | SSH service disabled/wrong port | Check SSH settings on device            |
| `AuthenticationException` | Wrong username/password         | Verify credentials                      |
| `TimeoutError`            | Network/device issues           | Check connectivity, increase timeout    |
| `SerialException`         | RS232 port issues               | Check port permissions, install drivers |
| `CommandError`            | Invalid command for device      | Check device compatibility/firmware     |
| `NotificationParseError`  | Malformed notification data     | Enable debug logging, report issue      |

Remember: Most issues are network or configuration related. Start with the basic connectivity test and work through the
specific error messages systematically.
