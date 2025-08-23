"""Streamlined network resilience tests for core clients."""

from unittest.mock import AsyncMock, patch

import pytest

from wyrestorm_networkhd.exceptions import ConnectionError


@pytest.mark.integration
class TestNetworkResilience:
    """Test network resilience and recovery patterns."""

    @pytest.mark.asyncio
    async def test_connection_retry_with_backoff(self, client):
        """Test connection retry with exponential backoff."""
        failure_count = 0

        async def mock_connect_with_failures():
            nonlocal failure_count
            failure_count += 1
            if failure_count < 3:
                raise ConnectionError("Connection failed")
            return True

        with patch.object(client, "connect", side_effect=mock_connect_with_failures):
            await client.reconnect(max_attempts=3, delay=0.01)
            assert failure_count == 3

    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_reconnection(self, client):
        """Test circuit breaker prevents connection attempts when open."""
        # Open circuit breaker
        for _ in range(3):
            client._record_failure()
        assert client._is_circuit_open()

        # Connection should be blocked
        with pytest.raises(ConnectionError, match="Circuit breaker is open"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self, client):
        """Test circuit breaker can be reset after failures."""
        # Open circuit breaker
        for _ in range(3):
            client._record_failure()
        assert client._is_circuit_open()

        # Reset and verify recovery
        client._reset_circuit()
        assert not client._is_circuit_open()
        assert client._failure_count == 0

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_errors(self, client, mock_connected_state):
        """Test graceful handling of various error conditions."""
        mock_connected_state(client)

        # Test timeout error
        with (
            patch.object(client, "_send_command_generic", new_callable=AsyncMock, side_effect=TimeoutError("Timeout")),
            pytest.raises(TimeoutError),
        ):
            await client.send_command("test", response_timeout=0.1)

        # Client should still be functional after timeout
        assert client.is_connected()  # Connection state unchanged

        # Test successful command after error
        with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value="OK"):
            response = await client.send_command("recovery_test")
            assert response == "OK"
