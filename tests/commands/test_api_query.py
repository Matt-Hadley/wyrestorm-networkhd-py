from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.api_query import APIQueryCommands
from wyrestorm_networkhd.exceptions import DeviceNotFoundError, DeviceQueryError


class TestAPIQueryCommands:
    """Unit tests for APIQueryCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = APIQueryCommands(self.mock_client)

    # =============================================================================
    # 13.1 Query Commands – System Configuration
    # =============================================================================

    @pytest.mark.asyncio
    async def test_config_get_version(self):
        """Test version query command."""
        # Arrange
        expected_response = "API version: v6.7\r\nSystem version: v1.0(v2.0)"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_version()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get version")
        assert result.api_version == "6.7"
        assert result.web_version == "1.0"
        assert result.core_version == "2.0"

    @pytest.mark.asyncio
    async def test_config_get_ipsetting(self):
        """Test IP setting query command."""
        # Arrange
        expected_response = "ipsetting is: ip4addr 192.168.1.100 netmask 255.255.255.0 gateway 192.168.1.1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_ipsetting()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get ipsetting")
        assert result.ip4addr == "192.168.1.100"
        assert result.netmask == "255.255.255.0"
        assert result.gateway == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_config_get_ipsetting2(self):
        """Test IP setting 2 query command."""
        # Arrange
        expected_response = "ipsetting2 is: ip4addr 10.0.0.50 netmask 255.255.255.0 gateway 10.0.0.1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_ipsetting2()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get ipsetting2")
        assert result.ip4addr == "10.0.0.50"
        assert result.netmask == "255.255.255.0"
        assert result.gateway == "10.0.0.1"

    @pytest.mark.asyncio
    async def test_config_get_devicelist(self):
        """Test device list query command."""
        # Arrange
        expected_response = "devicelist is TX1 RX1 TX2 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_devicelist()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get devicelist")
        assert result == ["TX1", "RX1", "TX2", "RX2"]

    @pytest.mark.asyncio
    async def test_config_get_devicelist_invalid_response(self):
        """Test device list query command with invalid response format."""
        # Arrange
        expected_response = "No devicelist here"
        self.mock_client.send_command.return_value = expected_response

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid devicelist response format"):
            await self.commands.config_get_devicelist()

        self.mock_client.send_command.assert_called_once_with("config get devicelist")

    @pytest.mark.asyncio
    async def test_config_get_devicejsonstring(self):
        """Test device JSON string query command."""
        # Arrange
        expected_response = """device json string:
[
    {
        "aliasName": "TX1",
        "deviceType": "Transmitter",
        "group": [{"name": "ungrouped", "sequence": 1}],
        "ip": "192.168.1.100",
        "online": true,
        "sequence": 1,
        "trueName": "TEST-TX1"
    }
]"""
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_devicejsonstring()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get devicejsonstring")
        assert len(result) == 1
        assert result[0].aliasName == "TX1"
        assert result[0].deviceType == "Transmitter"

    # =============================================================================
    # 13.2 Query Commands – Device Configuration
    # =============================================================================

    @pytest.mark.asyncio
    async def test_config_get_name_single_device(self):
        """Test device name query for single device."""
        # Arrange
        device = "TX1"
        expected_response = "TX1's alias is TestTransmitter"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_name(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get name TX1")
        assert result.hostname == "TX1"
        assert result.alias == "TestTransmitter"

    @pytest.mark.asyncio
    async def test_config_get_name_all_devices(self):
        """Test device name query for all devices."""
        # Arrange
        expected_response = "TX1's alias is TestTX\r\nRX1's alias is TestRX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_name()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get name")
        assert len(result) == 2
        assert result[0].hostname == "TX1"
        assert result[0].alias == "TestTX"

    @pytest.mark.asyncio
    async def test_config_get_name_device_not_found(self):
        """Test device name query with non-existent device raises DeviceNotFoundError."""
        # Arrange
        device = "InvalidDevice123"
        expected_response = '"InvalidDevice123" does not exist.'
        self.mock_client.send_command.return_value = expected_response

        # Act & Assert
        with pytest.raises(DeviceNotFoundError) as exc_info:
            await self.commands.config_get_name(device)

        assert exc_info.value.device_name == "InvalidDevice123"
        assert "InvalidDevice123" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_config_get_name_special_characters(self):
        """Test device name query with special characters raises DeviceNotFoundError."""
        # Arrange
        device = "Device@123"
        expected_response = '"Device@123" does not exist.'
        self.mock_client.send_command.return_value = expected_response

        # Act & Assert
        with pytest.raises(DeviceNotFoundError) as exc_info:
            await self.commands.config_get_name(device)

        assert exc_info.value.device_name == "Device@123"

    @pytest.mark.asyncio
    async def test_config_get_device_info_with_device(self):
        """Test device info query for specific device."""
        # Arrange
        device = "TX1"
        expected_response = """devices json info:
{
    "devices": [
        {
            "aliasname": "TX1",
            "name": "NHD-400-TX-TEST123"
        }
    ]
}"""
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_device_info(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get device info TX1", response_timeout=5)
        assert len(result) == 1
        assert result[0].aliasname == "TX1"

    @pytest.mark.asyncio
    async def test_config_get_device_info_all_devices(self):
        """Test device info query for all devices."""
        # Arrange
        expected_response = """devices json info:
{
    "devices": [
        {
            "aliasname": "TX1",
            "name": "NHD-400-TX-TEST123"
        },
        {
            "aliasname": "RX1",
            "name": "NHD-400-RX-TEST456"
        }
    ]
}"""
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_device_info()

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get device info", response_timeout=5)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_config_get_device_info_device_not_found(self):
        """Test device info query with non-existent device raises DeviceQueryError."""
        # Arrange
        device = "NonExistentTX1"
        expected_response = """devices json info:
{
    "devices" : [
        {
            "aliasname" : "",
            "error" : "no such device",
            "name" : "NonExistentTX1"
        }
    ]
}"""
        self.mock_client.send_command.return_value = expected_response

        # Act & Assert
        with pytest.raises(DeviceQueryError) as exc_info:
            await self.commands.config_get_device_info(device)

        assert exc_info.value.device_name == "NonExistentTX1"
        assert exc_info.value.error_message == "no such device"
        assert "NonExistentTX1" in str(exc_info.value)
        assert "no such device" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_config_get_device_status_with_device(self):
        """Test device status query for specific device."""
        # Arrange
        device = "RX1"
        expected_response = """devices status info:
{
    "devices status": [
        {
            "aliasname": "RX1",
            "name": "NHD-400-RX-TEST456",
            "hdmi out active": "true"
        }
    ]
}"""
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_get_device_status(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with("config get device status RX1")
        assert len(result) == 1
        assert result[0].aliasname == "RX1"

    @pytest.mark.asyncio
    async def test_config_get_device_status_device_not_found(self):
        """Test device status query with non-existent device raises DeviceQueryError."""
        # Arrange
        device = "InvalidRX999"
        expected_response = """devices status info:
{
    "devices status" : [
        {
            "aliasname" : "",
            "error" : "no such device",
            "name" : "InvalidRX999"
        }
    ]
}"""
        self.mock_client.send_command.return_value = expected_response

        # Act & Assert
        with pytest.raises(DeviceQueryError) as exc_info:
            await self.commands.config_get_device_status(device)

        assert exc_info.value.device_name == "InvalidRX999"
        assert exc_info.value.error_message == "no such device"

    # =============================================================================
    # 13.3 Query Commands – Stream Matrix Switching
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_get_all_devices(self):
        """Test matrix query for all devices."""
        # Arrange
        expected_response = "matrix information:\r\nTX1 RX1\r\nTX2 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix get")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX2"
        assert result.assignments[1].rx == "RX2"

    @pytest.mark.asyncio
    async def test_matrix_get_specific_devices(self):
        """Test matrix query for specific RX devices."""
        # Arrange
        rx_devices = ["RX1", "RX2"]
        expected_response = "matrix information:\r\nTX1 RX1\r\nTX2 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix get RX1 RX2")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX2"
        assert result.assignments[1].rx == "RX2"

    @pytest.mark.asyncio
    async def test_matrix_get_invalid_devices_empty_response(self):
        """Test matrix query with invalid devices returns empty assignments."""
        # Arrange
        rx_devices = ["InvalidRX1", "NonExistentRX2"]
        expected_response = "matrix information:\n\n"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix get InvalidRX1 NonExistentRX2")
        assert len(result.assignments) == 0  # Empty response should return empty list

    @pytest.mark.asyncio
    async def test_matrix_video_get_specific_devices(self):
        """Test matrix video query for specific RX devices."""
        # Arrange
        rx_devices = ["RX1", "RX2"]
        expected_response = "matrix video information:\r\nTX1 RX1\r\nTX2 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_video_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix video get RX1 RX2")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX2"
        assert result.assignments[1].rx == "RX2"

    @pytest.mark.asyncio
    async def test_matrix_video_get_all_devices(self):
        """Test matrix video query for all devices."""
        # Arrange
        expected_response = "matrix video information:\r\nTX1 RX1\r\nTX2 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_video_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix video get")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX2"
        assert result.assignments[1].rx == "RX2"

    @pytest.mark.asyncio
    async def test_matrix_audio_get_all_devices(self):
        """Test matrix audio query for all devices."""
        # Arrange
        expected_response = "matrix audio information:\r\nTX1 RX1\r\nTX2 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix audio get")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX2"
        assert result.assignments[1].rx == "RX2"

    @pytest.mark.asyncio
    async def test_matrix_audio_get_specific_devices(self):
        """Test matrix audio query for specific RX devices."""
        # Arrange
        rx_devices = ["RX1"]
        expected_response = "matrix audio information:\r\nTX1 RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix audio get RX1")
        assert len(result.assignments) == 1
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"

    @pytest.mark.asyncio
    async def test_matrix_audio2_get_all_devices(self):
        """Test matrix audio2 query for all devices."""
        # Arrange
        expected_response = "matrix audio2 information:\r\nTX1 RX1\r\nTX2 RX2\r\nNULL RX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio2_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix audio2 get")
        assert len(result.assignments) == 3
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX2"
        assert result.assignments[1].rx == "RX2"
        assert result.assignments[2].tx is None  # NULL connection
        assert result.assignments[2].rx == "RX3"

    @pytest.mark.asyncio
    async def test_matrix_audio2_get_specific_devices(self):
        """Test matrix audio2 query for specific RX devices."""
        # Arrange
        rx_devices = ["RX1", "RX2"]
        expected_response = "matrix audio2 information:\r\nTX1 RX1\r\nTX2 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio2_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix audio2 get RX1 RX2")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"

    @pytest.mark.asyncio
    async def test_matrix_audio3_get_no_params(self):
        """Test matrix audio3 query with no parameters."""
        # Arrange
        expected_response = "matrix audio3 information:\r\nRX1\r\nTX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio3_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix audio3 get")
        assert len(result.assignments) == 1
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[0].tx == "TX1"

    @pytest.mark.asyncio
    async def test_matrix_audio3_get_with_rx_only(self):
        """Test matrix audio3 query with RX device only."""
        # Arrange
        rx_device = "RX1"
        expected_response = "matrix audio3 information:\r\nRX1\r\nTX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio3_get(rx_device)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix audio3 get RX1")
        assert len(result.assignments) == 1
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[0].tx == "TX1"

    @pytest.mark.asyncio
    async def test_matrix_audio3_get_with_devices(self):
        """Test matrix audio3 query with RX and TX devices."""
        # Arrange
        rx_device = "RX1"
        tx_device = "TX1"
        expected_response = "matrix audio3 information:\r\nRX1\r\nTX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio3_get(rx_device, tx_device)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix audio3 get RX1 TX1")
        assert len(result.assignments) == 1
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[0].tx == "TX1"

    @pytest.mark.asyncio
    async def test_matrix_usb_get_all_devices(self):
        """Test matrix USB query for all devices."""
        # Arrange
        expected_response = "matrix usb information:\r\nTX1 RX1\r\nTX1 RX2\r\nTX2 RX3\r\nNULL RX4"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_usb_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix usb get")
        assert len(result.assignments) == 4
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX1"
        assert result.assignments[1].rx == "RX2"
        assert result.assignments[2].tx == "TX2"
        assert result.assignments[2].rx == "RX3"
        assert result.assignments[3].tx is None  # NULL connection
        assert result.assignments[3].rx == "RX4"

    @pytest.mark.asyncio
    async def test_matrix_usb_get_specific_devices(self):
        """Test matrix USB query for specific RX devices."""
        # Arrange
        rx_devices = ["RX1", "RX2"]
        expected_response = "matrix usb information:\r\nTX1 RX1\r\nTX1 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_usb_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix usb get RX1 RX2")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX1"
        assert result.assignments[1].rx == "RX2"

    @pytest.mark.asyncio
    async def test_matrix_infrared_get_all_devices(self):
        """Test matrix infrared query for all devices."""
        # Arrange
        expected_response = "matrix infrared information:\r\nTX1 RX1\r\nTX1 RX2\r\nTX2 RX3\r\nNULL RX4"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix infrared get")
        assert len(result.assignments) == 4
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX1"
        assert result.assignments[1].rx == "RX2"
        assert result.assignments[2].tx == "TX2"
        assert result.assignments[2].rx == "RX3"
        assert result.assignments[3].tx is None  # NULL connection
        assert result.assignments[3].rx == "RX4"

    @pytest.mark.asyncio
    async def test_matrix_infrared_get_specific_devices(self):
        """Test matrix infrared query for specific RX devices."""
        # Arrange
        rx_devices = ["RX1", "RX2"]
        expected_response = "matrix infrared information:\r\nTX1 RX1\r\nTX1 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix infrared get RX1 RX2")
        assert len(result.assignments) == 2
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX1"
        assert result.assignments[1].rx == "RX2"

    @pytest.mark.asyncio
    async def test_matrix_infrared2_get_all_devices(self):
        """Test matrix infrared2 query for all devices."""
        # Arrange
        expected_response = "matrix infrared2 information:\r\nTX1 single RX1\r\nRX2 api\r\nTX2 all\r\nRX3 null"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared2_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix infrared2 get")
        assert len(result.assignments) == 4
        assert result.assignments[0].device == "TX1"
        assert result.assignments[0].mode == "single"
        assert result.assignments[0].target_device == "RX1"
        assert result.assignments[1].device == "RX2"
        assert result.assignments[1].mode == "api"
        assert result.assignments[1].target_device is None

    @pytest.mark.asyncio
    async def test_matrix_infrared2_get_specific_devices(self):
        """Test matrix infrared2 query for specific devices."""
        # Arrange
        devices = ["TX1", "RX1"]
        expected_response = "matrix infrared2 information:\r\nTX1 single RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared2_get(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix infrared2 get TX1 RX1")
        assert len(result.assignments) == 1
        assert result.assignments[0].device == "TX1"
        assert result.assignments[0].mode == "single"
        assert result.assignments[0].target_device == "RX1"

    @pytest.mark.asyncio
    async def test_matrix_serial_get_all_devices(self):
        """Test matrix serial query for all devices."""
        # Arrange
        expected_response = "matrix serial information:\r\nTX1 RX1\r\nTX1 RX2\r\nTX2 RX3\r\nNULL RX4"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix serial get")
        assert len(result.assignments) == 4
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"
        assert result.assignments[1].tx == "TX1"
        assert result.assignments[1].rx == "RX2"
        assert result.assignments[2].tx == "TX2"
        assert result.assignments[2].rx == "RX3"
        assert result.assignments[3].tx is None  # NULL connection
        assert result.assignments[3].rx == "RX4"

    @pytest.mark.asyncio
    async def test_matrix_serial_get_specific_devices(self):
        """Test matrix serial query for specific RX devices."""
        # Arrange
        rx_devices = ["RX1"]
        expected_response = "matrix serial information:\r\nTX1 RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial_get(rx_devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix serial get RX1")
        assert len(result.assignments) == 1
        assert result.assignments[0].tx == "TX1"
        assert result.assignments[0].rx == "RX1"

    @pytest.mark.asyncio
    async def test_matrix_serial2_get_all_devices(self):
        """Test matrix serial2 query for all devices."""
        # Arrange
        expected_response = "matrix serial2 information:\r\nTX1 single RX1\r\nRX2 api\r\nTX2 all\r\nRX3 null"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial2_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix serial2 get")
        assert len(result.assignments) == 4
        assert result.assignments[0].device == "TX1"
        assert result.assignments[0].mode == "single"
        assert result.assignments[0].target_device == "RX1"
        assert result.assignments[1].device == "RX2"
        assert result.assignments[1].mode == "api"
        assert result.assignments[1].target_device is None

    @pytest.mark.asyncio
    async def test_matrix_serial2_get_specific_devices(self):
        """Test matrix serial2 query for specific devices."""
        # Arrange
        devices = ["TX1", "RX1"]
        expected_response = "matrix serial2 information:\r\nTX1 single RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial2_get(devices)

        # Assert
        self.mock_client.send_command.assert_called_once_with("matrix serial2 get TX1 RX1")
        assert len(result.assignments) == 1
        assert result.assignments[0].device == "TX1"
        assert result.assignments[0].mode == "single"
        assert result.assignments[0].target_device == "RX1"

    # =============================================================================
    # 13.4 Query Commands – Video Walls
    # =============================================================================

    @pytest.mark.asyncio
    async def test_scene_get(self):
        """Test video wall scene list query."""
        # Arrange
        expected_response = "scene list:\r\nVideoWall1-Scene1 VideoWall1-Scene2 VideoWall2-Scene1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.scene_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("scene get")
        assert len(result.scenes) == 3
        assert result.scenes[0].videowall == "VideoWall1"
        assert result.scenes[0].scene == "Scene1"
        assert result.scenes[1].videowall == "VideoWall1"
        assert result.scenes[1].scene == "Scene2"
        assert result.scenes[2].videowall == "VideoWall2"
        assert result.scenes[2].scene == "Scene1"

    @pytest.mark.asyncio
    async def test_vw_get(self):
        """Test video wall logical screen list query."""
        # Arrange
        expected_response = "Video wall information:\r\nVideoWall1-Scene1_Screen1 TX1\r\nRow 1: RX1 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.vw_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("vw get")
        assert len(result.logical_screens) >= 1
        assert result.logical_screens[0].videowall == "VideoWall1"
        assert result.logical_screens[0].scene == "Scene1"
        assert result.logical_screens[0].logical_screen == "Screen1"
        assert result.logical_screens[0].tx == "TX1"

    @pytest.mark.asyncio
    async def test_wscene2_get(self):
        """Test videowall within wall scene list query."""
        # Arrange
        expected_response = "wscene2 list:\r\nVideoWall1-WScene1 VideoWall1-WScene2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("wscene2 get")
        assert len(result.scenes) == 2
        assert result.scenes[0].videowall == "VideoWall1"
        assert result.scenes[0].scene == "WScene1"
        assert result.scenes[1].videowall == "VideoWall1"
        assert result.scenes[1].scene == "WScene2"

    # =============================================================================
    # 13.5 Query Commands – Multiview
    # =============================================================================

    @pytest.mark.asyncio
    async def test_mscene_get_all_devices(self):
        """Test preset multiview layout query for all devices."""
        # Arrange
        expected_response = "mscene list:\r\nRX1 Layout1 Layout2\r\nRX2 Layout3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("mscene get")
        assert len(result.multiview_layouts) == 2
        assert result.multiview_layouts[0].rx == "RX1"
        assert "Layout1" in result.multiview_layouts[0].layouts
        assert "Layout2" in result.multiview_layouts[0].layouts
        assert result.multiview_layouts[1].rx == "RX2"
        assert "Layout3" in result.multiview_layouts[1].layouts

    @pytest.mark.asyncio
    async def test_mscene_get_specific_rx(self):
        """Test preset multiview layout query for specific RX."""
        # Arrange
        rx = "RX1"
        expected_response = "mscene list:\r\nRX1 Layout1 Layout2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_get(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with("mscene get RX1")
        assert len(result.multiview_layouts) == 1
        assert result.multiview_layouts[0].rx == "RX1"
        assert "Layout1" in result.multiview_layouts[0].layouts
        assert "Layout2" in result.multiview_layouts[0].layouts

    @pytest.mark.asyncio
    async def test_mview_get_all_devices(self):
        """Test custom multiview layout query for all devices."""
        # Arrange
        expected_response = "mview information:\r\nRX1 tile TX1:0_0_960_540:fit TX2:960_0_960_540:stretch"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_get()

        # Assert
        self.mock_client.send_command.assert_called_once_with("mview get")
        assert len(result.configurations) == 1
        assert result.configurations[0].rx == "RX1"
        assert result.configurations[0].mode == "tile"
        assert len(result.configurations[0].tiles) == 2
        assert result.configurations[0].tiles[0].tx == "TX1"
        assert result.configurations[0].tiles[0].x == 0
        assert result.configurations[0].tiles[0].y == 0

    @pytest.mark.asyncio
    async def test_mview_get_specific_rx(self):
        """Test custom multiview layout query for specific RX."""
        # Arrange
        rx = "RX2"
        expected_response = "mview information:\r\nRX2 overlay TX1:100_100_800_600:fit"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_get(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with("mview get RX2")
        assert len(result.configurations) == 1
        assert result.configurations[0].rx == "RX2"
        assert result.configurations[0].mode == "overlay"
        assert len(result.configurations[0].tiles) == 1
        assert result.configurations[0].tiles[0].tx == "TX1"
        assert result.configurations[0].tiles[0].scaling == "fit"

    @pytest.mark.asyncio
    async def test_mscene_get_invalid_rx_empty_response(self):
        """Test mscene get with invalid RX returns empty layouts."""
        # Arrange
        rx = "InvalidRX123"
        expected_response = "mscene list:\n\n"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_get(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with("mscene get InvalidRX123")
        assert len(result.multiview_layouts) == 0

    @pytest.mark.asyncio
    async def test_mview_get_invalid_decoder_empty_response(self):
        """Test mview get with invalid decoder returns empty configurations."""
        # Arrange
        rx = "NonExistentDecoder"
        expected_response = "mview information:\n\n"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_get(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with("mview get NonExistentDecoder")
        assert len(result.configurations) == 0
