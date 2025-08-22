# WyreStorm NetworkHD API Client

[![PyPI version](https://badge.fury.io/py/wyrestorm-networkhd.svg)](https://badge.fury.io/py/wyrestorm-networkhd)
[![Python Support](https://img.shields.io/pypi/pyversions/wyrestorm-networkhd.svg)](https://pypi.org/project/wyrestorm-networkhd/)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Matt-Hadley/8f4a6e65e2d520f63a82a34cddcc4b56/raw/coverage.json)](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python client library for interacting with WyreStorm NetworkHD API operations. Supports all major command categories
including matrix switching, device control, video walls, multiview, and more.

## Installation

```bash
pip install wyrestorm-networkhd
```

## Quick Start

```python
from wyrestorm_networkhd import NetworkHDClient, ConnectionType, NHDAPI

# Create client with SSH connection
client = NetworkHDClient(
    connection_type=ConnectionType.SSH,
    host="192.168.1.100",
    port=10022,
    username="wyrestorm",
    password="networkhd"
)

# Use with context manager
async with client:
    # Create API wrapper
    api = NHDAPI(client)

    # Execute commands and get typed responses
    device_list = await api.api_query.get_devicelist()
    matrix_info = await api.api_query.matrix_get()
    await api.video_wall.scene_active("office", "splitmode")
```

## Features

- **Strongly Typed**: Full type hints and data models for all API responses
- **Async/Await Support**: Built for modern Python async applications
- **Multiple Connection Types**: SSH connections supported, but extensible for other connection types in the future
  (RS232, Telnet) if required.
- **Comprehensive API Coverage**: All NetworkHD API commands supported
- **Error Handling**: Robust error handling with custom exception types
- **Context Manager Support**: Clean resource management

## API Categories

API categories match those in the API Reference (see below).

- **System Configuration**: Version info, IP settings, device lists
- **Device Configuration**: Device names, info, and status
- **Matrix Switching**: Video, audio, USB, infrared, and serial routing
- **Video Walls**: Scene management and logical screen control
- **Multiview**: Preset and custom layout management
- **Device Control**: Reboot, reset, and port switching
- **Notifications**: Real-time device status updates

## Logging

The package includes comprehensive logging for debugging and monitoring. Logging is configured automatically but can be
customized.

### Default Logging

By default, logs are output to the console at INFO level. The following events are logged:

- **INFO**: Connection establishment/disconnection, command execution
- **DEBUG**: Detailed command/response data, SSH connection details
- **ERROR**: Connection failures, command errors

### Customizing Logging

```python
from wyrestorm_networkhd.logging_config import setup_logging

# Set debug level for verbose output
setup_logging(level="DEBUG")

# Log to file
setup_logging(level="INFO", log_file="logs/wyrestorm_networkhd.log")

# Custom format
setup_logging(
    level="DEBUG",
    log_format="%(levelname)s - %(name)s - %(message)s"
)
```

### Log Levels

- **DEBUG**: All details including commands, responses, and SSH operations
- **INFO**: Connection events and command execution (default)
- **WARNING**: Non-critical issues
- **ERROR**: Errors and failures
- **CRITICAL**: Critical system failures

### Environment Variables

Set `LOG_LEVEL` environment variable to control logging level:

```bash
export LOG_LEVEL=DEBUG
python your_script.py
```

## Security Configuration

The client supports configurable SSH host key verification policies to balance security with usability in different
deployment scenarios.

### Host Key Verification Policies

- **`HostKeyPolicy.WARN`** (default): Warns about unknown hosts but continues
  - Good balance between security and usability
  - Provides visibility into security issues
  - Suitable for production with monitoring

- **`HostKeyPolicy.REJECT`**: Rejects connections to unknown hosts
  - Most secure option for production environments
  - Requires known host keys to be pre-configured
  - Best for environments with stable, known devices

- **`HostKeyPolicy.AUTO_ADD`**: Automatically trusts unknown host keys
  - Good for development and testing environments
  - ⚠️ **Security Warning**: Vulnerable to man-in-the-middle attacks
  - Use only in controlled, trusted environments

- **`HostKeyPolicy.ASK`**: Prompts user for confirmation
  - Interactive mode for development/testing
  - Requires user interaction in terminal
  - Good for controlled testing environments

### Usage Examples

```python
from wyrestorm_networkhd import NetworkHDClient, HostKeyPolicy, ConnectionType

# Default behavior (WARN policy)
client = NetworkHDClient(
    connection_type=ConnectionType.SSH,
    host="192.168.1.100",
    password="secret"
)

# Secure production setup
client = NetworkHDClient(
    connection_type=ConnectionType.SSH,
    host="192.168.1.100",
    password="secret",
    ssh_host_key_policy=HostKeyPolicy.REJECT
)

# Auto-add mode for development/testing
client = NetworkHDClient(
    connection_type=ConnectionType.SSH,
    host="192.168.1.100",
    password="secret",
    ssh_host_key_policy=HostKeyPolicy.AUTO_ADD
)
```

### Security Recommendations

- **Production Environments**: Use `REJECT` or `WARN` policies (WARN is default)
- **Development/Testing**: Use `AUTO_ADD` or `ASK` policies
- **Controlled Networks**: `AUTO_ADD` may be acceptable if network security is assured
- **Monitor Logs**: Always monitor logs for security warnings when using permissive policies
- **Default Behavior**: New clients now use WARN policy by default for better security

## 🧪 Testing

This project uses pytest for comprehensive testing with coverage reporting.

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# For verbose output
VERBOSE=1 make test
```

### Test Categories

- **Unit Tests**: Test individual functions and classes in isolation
- **Benchmark Tests** (`@pytest.mark.benchmark`): Performance testing

### VS Code Integration

The project includes VS Code configuration for:

- **Testing Panel**: Run and debug tests directly in the editor
- **Coverage Display**: Visual coverage indicators in the gutter
- **Debug Configurations**: Debug tests with breakpoints
- **Tasks**: Quick access to common testing operations

Install the recommended extensions and reload VS Code to enable testing features.

## 🚀 Development

### Quick Setup

```bash
git clone https://github.com/Matt-Hadley/wyrestorm-networkhd-py.git
cd wyrestorm-networkhd
make install
```

### Development Commands

```bash
# Essential commands
make install          # Setup development environment
make dev-workflow     # Format, lint, and test (daily development)
make test             # Run tests
make check            # Code quality checks
make build            # Build package
make health-check     # Full project validation

# See all commands
make help
```

### Daily Workflow

```bash
# Setup once
make install

# Daily development
make dev-workflow     # Format → Lint → Test

# Before committing
make check

# Before release
make release
```

### Additional Tools

```bash
# Pre-commit hooks (automatic with make install)
make pre-commit

# Comprehensive validation
make health-check

# Verbose output
VERBOSE=1 make test
```

## 📚 Documentation

Documentation is available in the source code through comprehensive docstrings and type hints. Key documentation
sources:

- **README.md**: This file - installation, usage, and examples
- **example.py**: Complete usage examples
- **Source code**: Comprehensive docstrings and type hints
- **Tests**: Usage examples in the test files

For the official WyreStorm API reference, see the `docs/NetworkHD_API_v6.7.pdf` file included with this project or visit
[WyreStorm Support](https://support.wyrestorm.com/network-hd/api-and-control-drivers).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
