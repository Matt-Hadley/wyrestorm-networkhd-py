from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.connected_device_control import ConnectedDeviceControlCommands


class TestConnectedDeviceControlCommands:
    """Unit tests for ConnectedDeviceControlCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = ConnectedDeviceControlCommands(self.mock_client)

    # =============================================================================
    # 8.1 Device Control – Proxy Commands
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_sinkpower_on_single_rx(self):
        """Test setting device sinkpower on for single RX."""
        # Arrange
        power = "on"
        rx = "RX1"
        expected_command = "config set device sinkpower on RX1"
        expected_response = "config set device sinkpower on RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_sinkpower(power, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_sinkpower_off_single_rx(self):
        """Test setting device sinkpower off for single RX."""
        # Arrange
        power = "off"
        rx = "Display1"
        expected_command = "config set device sinkpower off Display1"
        expected_response = "config set device sinkpower off Display1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_sinkpower(power, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_sinkpower_multiple_rx(self):
        """Test setting device sinkpower for multiple RX devices."""
        # Arrange
        power = "on"
        rx_list = ["RX1", "RX2", "RX3"]
        expected_command = "config set device sinkpower on RX1 RX2 RX3"
        expected_response = "config set device sinkpower on RX1 RX2 RX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_sinkpower(power, rx_list)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_sinkpower_with_command_echo(self):
        """Test setting device sinkpower with command echo in response."""
        # Arrange
        power = "off"
        rx = "RX1"
        expected_command = "config set device sinkpower off RX1"
        expected_response = "config set device sinkpower off RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_sinkpower(power, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_onetouchplay_single_rx(self):
        """Test setting device CEC one-touch-play for single RX."""
        # Arrange
        command_type = "onetouchplay"
        rx = "RX1"
        expected_command = "config set device cec onetouchplay RX1"
        expected_response = "config set device cec onetouchplay RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec(command_type, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_standby_single_rx(self):
        """Test setting device CEC standby for single RX."""
        # Arrange
        command_type = "standby"
        rx = "Display2"
        expected_command = "config set device cec standby Display2"
        expected_response = "config set device cec standby Display2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec(command_type, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_multiple_rx(self):
        """Test setting device CEC for multiple RX devices."""
        # Arrange
        command_type = "onetouchplay"
        rx_list = ["RX1", "RX2", "Display1"]
        expected_command = "config set device cec onetouchplay RX1 RX2 Display1"
        expected_response = "config set device cec onetouchplay RX1 RX2 Display1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec(command_type, rx_list)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    # =============================================================================
    # 8.2 Device Control – Custom Command Generation
    # =============================================================================

    @pytest.mark.asyncio
    async def test_cec_command(self):
        """Test sending custom CEC command."""
        # Arrange
        cecdata = "04820000"
        rx = "RX1"
        expected_command = 'cec "04820000" RX1'
        expected_response = 'cec "04820000" RX1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.cec(cecdata, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_cec_command_with_longer_data(self):
        """Test sending custom CEC command with longer data."""
        # Arrange
        cecdata = "04823600000000000000"
        rx = "Display1"
        expected_command = 'cec "04823600000000000000" Display1'
        expected_response = 'cec "04823600000000000000" Display1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.cec(cecdata, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_infrared_command_rx(self):
        """Test sending custom infrared command to RX."""
        # Arrange
        irdata = "0000 006C 0022 0002 015B 00AD 0016 0016 0016 0016 0016 0041 0016 0041 0016 0041"
        device = "RX1"
        expected_command = (
            'infrared "0000 006C 0022 0002 015B 00AD 0016 0016 0016 0016 0016 0041 0016 0041 0016 0041" RX1'
        )
        expected_response = (
            'infrared "0000 006C 0022 0002 015B 00AD 0016 0016 0016 0016 0016 0041 0016 0041 0016 0041" RX1'
        )
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.infrared(irdata, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_infrared_command_tx(self):
        """Test sending custom infrared command to TX."""
        # Arrange
        irdata = "0000 006C 0000 0022 00AD"
        device = "TX1"
        expected_command = 'infrared "0000 006C 0000 0022 00AD" TX1'
        expected_response = 'infrared "0000 006C 0000 0022 00AD" TX1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.infrared(irdata, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_serial_command_basic_ascii(self):
        """Test sending basic RS-232 command in ASCII format."""
        # Arrange
        baud = 9600
        bits = 8
        parity = "n"
        stop = 1
        cr = True
        lf = False
        hex_format = False
        data = "POWER ON"
        device = "RX1"
        expected_command = 'serial -b 9600-8n1 -r on -n off -h off "POWER ON" RX1'
        expected_response = 'serial -b 9600-8n1 -r on -n off -h off "POWER ON" RX1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.serial(baud, bits, parity, stop, cr, lf, hex_format, data, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_serial_command_hex_format(self):
        """Test sending RS-232 command in hexadecimal format."""
        # Arrange
        baud = 19200
        bits = 7
        parity = "e"
        stop = 2
        cr = False
        lf = True
        hex_format = True
        data = "01 02 03 FF"
        device = "TX1"
        expected_command = 'serial -b 19200-7e2 -r off -n on -h on "01 02 03 FF" TX1'
        expected_response = 'serial -b 19200-7e2 -r off -n on -h on "01 02 03 FF" TX1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.serial(baud, bits, parity, stop, cr, lf, hex_format, data, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_serial_command_odd_parity(self):
        """Test sending RS-232 command with odd parity."""
        # Arrange
        baud = 115200
        bits = 6
        parity = "o"
        stop = 1
        cr = True
        lf = True
        hex_format = False
        data = "STATUS?"
        device = "Display1"
        expected_command = 'serial -b 115200-6o1 -r on -n on -h off "STATUS?" Display1'
        expected_response = 'serial -b 115200-6o1 -r on -n on -h off "STATUS?" Display1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.serial(baud, bits, parity, stop, cr, lf, hex_format, data, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_serial_command_no_delimiters(self):
        """Test sending RS-232 command with no delimiters."""
        # Arrange
        baud = 2400
        bits = 8
        parity = "n"
        stop = 1
        cr = False
        lf = False
        hex_format = False
        data = "TEST"
        device = "RX2"
        expected_command = 'serial -b 2400-8n1 -r off -n off -h off "TEST" RX2'
        expected_response = 'serial -b 2400-8n1 -r off -n off -h off "TEST" RX2'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.serial(baud, bits, parity, stop, cr, lf, hex_format, data, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_serial_command_high_baud_rate(self):
        """Test sending RS-232 command with high baud rate."""
        # Arrange
        baud = 57600
        bits = 8
        parity = "n"
        stop = 2
        cr = True
        lf = False
        hex_format = True
        data = "AA BB CC DD"
        device = "TX2"
        expected_command = 'serial -b 57600-8n2 -r on -n off -h on "AA BB CC DD" TX2'
        expected_response = 'serial -b 57600-8n2 -r on -n off -h on "AA BB CC DD" TX2'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.serial(baud, bits, parity, stop, cr, lf, hex_format, data, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    # =============================================================================
    # Edge Cases and Error Scenarios
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_sinkpower_empty_rx_list(self):
        """Test setting device sinkpower with empty RX list."""
        # Arrange
        power = "on"
        rx_list = []
        expected_command = "config set device sinkpower on "
        expected_response = "config set device sinkpower on"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_sinkpower(power, rx_list)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_cec_with_whitespace_in_response(self):
        """Test setting device CEC with whitespace in response."""
        # Arrange
        command_type = "standby"
        rx = "RX1"
        expected_command = "config set device cec standby RX1"
        expected_response = "  config set device cec standby RX1  "
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_cec(command_type, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_cec_command_with_special_characters_in_device(self):
        """Test CEC command with special characters in device name."""
        # Arrange
        cecdata = "04820000"
        rx = "RX-Display_1"
        expected_command = 'cec "04820000" RX-Display_1'
        expected_response = 'cec "04820000" RX-Display_1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.cec(cecdata, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_infrared_command_with_empty_data(self):
        """Test infrared command with empty data."""
        # Arrange
        irdata = ""
        device = "RX1"
        expected_command = 'infrared "" RX1'
        expected_response = 'infrared "" RX1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.infrared(irdata, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_serial_command_with_quotes_in_data(self):
        """Test serial command with quotes in data."""
        # Arrange
        baud = 9600
        bits = 8
        parity = "n"
        stop = 1
        cr = False
        lf = False
        hex_format = False
        data = 'TEST "DATA" STRING'
        device = "RX1"
        expected_command = 'serial -b 9600-8n1 -r off -n off -h off "TEST "DATA" STRING" RX1'
        expected_response = 'serial -b 9600-8n1 -r off -n off -h off "TEST "DATA" STRING" RX1'
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.serial(baud, bits, parity, stop, cr, lf, hex_format, data, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
