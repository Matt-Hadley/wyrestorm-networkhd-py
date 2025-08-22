from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.api_notifications import APINotificationsCommands


class TestAPINotificationsCommands:
    """Unit tests for APINotificationsCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = APINotificationsCommands(self.mock_client)

    # =============================================================================
    # 12.1 Enable / Disable Notifications
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_on_single_device(self):
        """Test enabling CEC notifications for single device."""
        # Arrange
        state = "on"
        device = "TX1"
        expected_command = "config set device cec notify on TX1"
        expected_response = "config set device cec notify on TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_off_single_device(self):
        """Test disabling CEC notifications for single device."""
        # Arrange
        state = "off"
        device = "RX2"
        expected_command = "config set device cec notify off RX2"
        expected_response = "config set device cec notify off RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_multiple_devices(self):
        """Test enabling CEC notifications for multiple devices."""
        # Arrange
        state = "on"
        devices = ["TX1", "RX1", "TX2"]
        expected_command = "config set device cec notify on TX1 RX1 TX2"
        expected_response = "config set device cec notify on TX1 RX1 TX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_all_devices(self):
        """Test enabling CEC notifications for all devices."""
        # Arrange
        state = "on"
        devices = "ALL_DEV"
        expected_command = "config set device cec notify on ALL_DEV"
        expected_response = "config set device cec notify on ALL_DEV"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_all_tx(self):
        """Test enabling CEC notifications for all transmitters."""
        # Arrange
        state = "off"
        devices = "ALL_TX"
        expected_command = "config set device cec notify off ALL_TX"
        expected_response = "config set device cec notify off ALL_TX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_all_rx(self):
        """Test enabling CEC notifications for all receivers."""
        # Arrange
        state = "on"
        devices = "ALL_RX"
        expected_command = "config set device cec notify on ALL_RX"
        expected_response = "config set device cec notify on ALL_RX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_with_multiline_response(self):
        """Test CEC notifications with multiline response."""
        # Arrange
        state = "on"
        devices = ["TX-Main", "RX-Display1"]
        expected_command = "config set device cec notify on TX-Main RX-Display1"
        expected_response = (
            "config set device cec notify on TX-Main RX-Display1\nCEC notifications enabled successfully"
        )
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_notify_with_whitespace_response(self):
        """Test CEC notifications with whitespace in response."""
        # Arrange
        state = "off"
        device = "RX1"
        expected_command = "config set device cec notify off RX1"
        expected_response = "  config set device cec notify off RX1  "
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec_notify(state, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
