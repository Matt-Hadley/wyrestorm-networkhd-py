# Core Module Tests

This directory contains tests for the core networking clients (SSH and RS232) that form the foundation of the WyreStorm
NetworkHD library.

## Test Architecture

The core tests are organized using a **consolidated architecture** that eliminates redundancy while maintaining
comprehensive coverage across both client types.

### File Structure

```
tests/core/
├── test_fixtures.py                 # Shared fixtures and mock infrastructure
├── test_base_client.py              # Base test mixins for common behavior
├── test_client_common.py            # Parametrized tests for both client types
├── test_integration_consolidated.py # Cross-client integration tests
├── test_protocol_integration.py     # Protocol-specific behavior tests
├── test_network_resilience.py       # Network resilience and recovery tests
└── README.md                        # This file
```

## Test Organization

### 1. Shared Infrastructure (`test_fixtures.py`)

Contains reusable fixtures and mock objects:

- **Client Fixtures**: `ssh_client`, `rs232_client`, `client` (parametrized)
- **Mock Infrastructure**: `mock_ssh_complete`, `mock_serial_complete`
- **Helper Fixtures**: `mock_connected_state` for simulating connected clients

```python
# Use parametrized client fixture for tests that work with both types
def test_common_behavior(client):
    """Test works with both SSH and RS232 clients."""
    assert client.get_connection_state() == "disconnected"
```

### 2. Base Test Classes (`test_base_client.py`)

Provides **test mixins** for common client behaviors:

- **`BaseClientTestMixin`**: Core client functionality (state, metrics, circuit breaker)
- **`BaseConnectionTestMixin`**: Connection lifecycle tests
- **`BaseCommandTestMixin`**: Command execution tests

```python
class MyTestClass(BaseClientTestMixin):
    """Inherit common test methods automatically."""
    pass
```

### 3. Common Client Tests (`test_client_common.py`)

**Parametrized tests** that run against both SSH and RS232 clients:

- **Initialization**: Parameter validation, default values
- **Connection Management**: Connect/disconnect, context managers
- **Command Execution**: Success/failure scenarios, timeouts
- **Message Dispatching**: Start/stop behavior

```python
@pytest.mark.unit
class TestClientConnection(BaseConnectionTestMixin):
    @pytest.mark.asyncio
    async def test_connect_success(self, client):
        """Test runs for both SSH and RS232."""
        # Test implementation works with both client types
```

### 4. Integration Tests (`test_integration_consolidated.py`)

**Cross-client integration tests** that verify consistent behavior:

- **Full Lifecycle**: Complete connect → command → disconnect workflows
- **Notification Handling**: Callback registration and message processing
- **Error Recovery**: Failure scenarios and resilience patterns
- **Performance Metrics**: Metrics tracking across operations

### 5. Protocol-Specific Tests (`test_protocol_integration.py`)

Tests for **protocol differences** and edge cases:

- **SSH-Specific**: Host key policies, transport lifecycle, shell management
- **RS232-Specific**: Baudrate handling, serial parameters, port availability
- **Protocol Consistency**: Ensures same commands work across both transports

### 6. Network Resilience Tests (`test_network_resilience.py`)

Tests for **network reliability** and recovery:

- **Connection Retry**: Exponential backoff, max attempts
- **Circuit Breaker**: Failure thresholds, auto-recovery
- **Graceful Degradation**: Error handling without state corruption

## Running Tests

### Run All Core Tests

```bash
pytest tests/core/ -v
```

### Run by Category

```bash
# Unit tests only
pytest tests/core/ -m unit

# Integration tests only
pytest tests/core/ -m integration

# Protocol-specific tests
pytest tests/core/test_protocol_integration.py
```

### Run by Client Type

```bash
# SSH client tests
pytest tests/core/ -k ssh

# RS232 client tests
pytest tests/core/ -k rs232
```

## Test Patterns

### Parametrized Client Testing

Most tests use the `client` fixture which automatically runs tests against both SSH and RS232:

```python
def test_both_clients(client):
    """Automatically tests both SSH and RS232 clients."""
    assert not client.is_connected()
    # Test logic works for both client types
```

### Protocol-Specific Testing

When testing protocol differences, branch based on client type:

```python
def test_protocol_specific(client):
    if hasattr(client, 'host'):  # SSH client
        # SSH-specific test logic
        assert client.ssh_host_key_policy in ["auto_add", "reject", "warn"]
    else:  # RS232 client
        # RS232-specific test logic
        assert client.baudrate > 0
```

### Mock Usage

Use the comprehensive mock fixtures to avoid repetitive setup:

```python
def test_with_mocks(client, mock_connected_state):
    """Use shared mock infrastructure."""
    mock_connected_state(client)
    assert client.is_connected()
```

## Test Markers

- **`@pytest.mark.unit`**: Fast, isolated unit tests
- **`@pytest.mark.integration`**: Integration tests with external dependencies
- **`@pytest.mark.asyncio`**: Async tests (most core tests)

## Coverage Focus

The core tests prioritize:

1. **Behavior Testing**: Focus on client behavior, not implementation details
2. **Error Scenarios**: Comprehensive failure mode testing
3. **Cross-Client Consistency**: Ensure both protocols behave identically
4. **Edge Cases**: Network failures, malformed data, resource exhaustion

## Adding New Tests

### For Common Behavior

Add to `test_client_common.py` using the parametrized `client` fixture.

### For Protocol Differences

Add to `test_protocol_integration.py` with client-type branching.

### For Integration Scenarios

Add to `test_integration_consolidated.py` for cross-component workflows.

### For New Mock Objects

Add to `test_fixtures.py` and make them available as fixtures.

## Maintenance Notes

- **Keep DRY**: Use fixtures and mixins to avoid code duplication
- **Protocol Agnostic**: Write tests that work with both client types when possible
- **Focus on Behavior**: Test what the client does, not how it's implemented
- **Mock Comprehensively**: Use the shared mock infrastructure for consistency
