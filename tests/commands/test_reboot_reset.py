from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.reboot_reset import RebootResetCommands


class TestRebootResetCommands:
    """Unit tests for RebootResetCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = RebootResetCommands(self.mock_client)

    # =============================================================================
    # 5.1 Device Reboot
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_reboot(self):
        """Test rebooting the NHD-CTL."""
        # Arrange
        expected_response = "system will reboot now"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.set_reboot()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config set reboot")
        assert result is True

    @pytest.mark.asyncio
    async def test_set_reboot_with_additional_output(self):
        """Test rebooting the NHD-CTL with additional output."""
        # Arrange
        expected_response = "Preparing for reboot... system will reboot now. Please wait."
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.set_reboot()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config set reboot")
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_reboot_single_device_string(self):
        """Test rebooting a single device passed as string."""
        # Arrange
        device = "TX1"
        expected_response = "the following device will reboot now: TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.set_device_reboot(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with("config set device reboot TX1", response_timeout=10.0)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_reboot_single_device_list(self):
        """Test rebooting a single device passed as list."""
        # Arrange
        devices = ["RX2"]
        expected_response = "the following device will reboot now: RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.set_device_reboot(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("config set device reboot RX2", response_timeout=10.0)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_reboot_multiple_devices(self):
        """Test rebooting multiple devices."""
        # Arrange
        devices = ["TX1", "RX1", "TX2"]
        expected_response = "the following device will reboot now: TX1 RX1 TX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.set_device_reboot(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(
            "config set device reboot TX1 RX1 TX2", response_timeout=10.0
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_reboot_with_additional_output(self):
        """Test rebooting devices with additional output in response."""
        # Arrange
        devices = ["TX-Main", "RX-Display"]
        expected_response = "Preparing to reboot devices... the following device will reboot now: TX-Main RX-Display. Estimated time: 30 seconds."
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.set_device_reboot(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(
            "config set device reboot TX-Main RX-Display", response_timeout=10.0
        )
        assert result is True

    # =============================================================================
    # 5.2 Device Reset
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_restorefactory_single_device_string(self):
        """Test factory reset of a single device passed as string."""
        # Arrange
        device = "TX1"
        expected_response = "the following device will restore now: TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_restorefactory(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(
            "config set device restorefactory TX1", response_timeout=10.0
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_restorefactory_single_device_list(self):
        """Test factory reset of a single device passed as list."""
        # Arrange
        devices = ["RX2"]
        expected_response = "the following device will restore now: RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_restorefactory(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(
            "config set device restorefactory RX2", response_timeout=10.0
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_restorefactory_multiple_devices(self):
        """Test factory reset of multiple devices."""
        # Arrange
        devices = ["TX1", "RX1", "TX2"]
        expected_response = "the following device will restore now: TX1 RX1 TX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_restorefactory(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(
            "config set device restorefactory TX1 RX1 TX2", response_timeout=10.0
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_restorefactory_with_additional_output(self):
        """Test factory reset with additional output in response."""
        # Arrange
        devices = ["TX-Main", "RX-Display"]
        expected_response = "Preparing to restore factory settings... the following device will restore now: TX-Main RX-Display. This operation cannot be undone."
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_restorefactory(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with(
            "config set device restorefactory TX-Main RX-Display", response_timeout=10.0
        )
        assert result is True
