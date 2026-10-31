import pytest

from tests.commands import echoing_client
from wyrestorm_networkhd.commands.reboot_reset import RebootResetCommands


class TestRebootResetCommands:
    """Unit tests for RebootResetCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = echoing_client()
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
        self.mock_client.send_command.assert_called_once_with("config set device reboot TX1")
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
        self.mock_client.send_command.assert_called_once_with("config set device reboot RX2")
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
        self.mock_client.send_command.assert_called_once_with("config set device reboot TX1 RX1 TX2")
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
        self.mock_client.send_command.assert_called_once_with("config set device reboot TX-Main RX-Display")
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
        self.mock_client.send_command.assert_called_once_with("config set device restorefactory TX1")
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
        self.mock_client.send_command.assert_called_once_with("config set device restorefactory RX2")
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
        self.mock_client.send_command.assert_called_once_with("config set device restorefactory TX1 RX1 TX2")
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
        self.mock_client.send_command.assert_called_once_with("config set device restorefactory TX-Main RX-Display")
        assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["set_device_reboot", "config_set_device_restorefactory"])
async def test_empty_device_list_is_rejected(method):
    """With no device named nothing is sent, as the API doesn't define the command without one."""
    client = echoing_client()
    with pytest.raises(ValueError):
        await getattr(RebootResetCommands(client), method)([])
    client.send_command.assert_not_called()
