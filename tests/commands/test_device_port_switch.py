from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.device_port_switch import DevicePortSwitchCommands


class TestDevicePortSwitchCommands:
    """Unit tests for DevicePortSwitchCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = DevicePortSwitchCommands(self.mock_client)

    # =============================================================================
    # 7.1 Port Switching – Video
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_videosource_auto(self):
        """Test setting device video source to auto."""
        # Arrange
        tx = "TX1"
        source = "auto"
        expected_command = "config set device videosource TX1 auto"
        expected_response = "config set device videosource TX1 auto"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_videosource(tx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_videosource_hdmi(self):
        """Test setting device video source to HDMI."""
        # Arrange
        tx = "Source1"
        source = "hdmi"
        expected_command = "config set device videosource Source1 hdmi"
        expected_response = "config set device videosource Source1 hdmi"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_videosource(tx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_videosource_dp(self):
        """Test setting device video source to DisplayPort."""
        # Arrange
        tx = "TX-Encoder"
        source = "dp"
        expected_command = "config set device videosource TX-Encoder dp"
        expected_response = "config set device videosource TX-Encoder dp"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_videosource(tx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_video_source_switch_hdmi(self):
        """Test setting device info video source switch to HDMI."""
        # Arrange
        source = "hdmi"
        tx = "TX1"
        expected_command = "config set device info video_source_switch=hdmi TX1"
        expected_response = "config set device info video_source_switch=hdmi TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_video_source_switch(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_video_source_switch_usb_c(self):
        """Test setting device info video source switch to USB-C."""
        # Arrange
        source = "usb-c"
        tx = "Source2"
        expected_command = "config set device info video_source_switch=usb-c Source2"
        expected_response = "config set device info video_source_switch=usb-c Source2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_video_source_switch(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_video_source_switch_none(self):
        """Test setting device info video source switch to none (audio only)."""
        # Arrange
        source = "none"
        tx = "TX-AudioOnly"
        expected_command = "config set device info video_source_switch=none TX-AudioOnly"
        expected_response = "config set device info video_source_switch=none TX-AudioOnly"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_video_source_switch(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    # =============================================================================
    # 7.2 Port Switching – Audio
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_audiosource_hdmi(self):
        """Test setting device audio source to HDMI."""
        # Arrange
        rx = "RX1"
        source = "hdmi"
        expected_command = "config set device audiosource RX1 hdmi"
        expected_response = "config set device audiosource RX1 hdmi"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audiosource(rx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audiosource_dmix(self):
        """Test setting device audio source to downmix."""
        # Arrange
        rx = "Display1"
        source = "dmix"
        expected_command = "config set device audiosource Display1 dmix"
        expected_response = "config set device audiosource Display1 dmix"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audiosource(rx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audiosource_analog(self):
        """Test setting device audio source to analog."""
        # Arrange
        rx = "RX-Main"
        source = "analog"
        expected_command = "config set device audiosource RX-Main analog"
        expected_response = "config set device audiosource RX-Main analog"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audiosource(rx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio2source_analog(self):
        """Test setting device audio2 source to analog."""
        # Arrange
        rx = "RX1"
        stream = "analog"
        expected_command = "config set device audio2source RX1 analog"
        expected_response = "config set device audio2source RX1 analog"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio2source(rx, stream)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio2source_dmix(self):
        """Test setting device audio2 source to downmix."""
        # Arrange
        rx = "Display2"
        stream = "dmix"
        expected_command = "config set device audio2source Display2 dmix"
        expected_response = "config set device audio2source Display2 dmix"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio2source(rx, stream)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_input_type_auto(self):
        """Test setting device audio input type to auto."""
        # Arrange
        source = "auto"
        tx = "TX1"
        expected_command = "config set device audio input type auto TX1"
        expected_response = "config set device audio input type auto TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_input_type(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_input_type_hdmi(self):
        """Test setting device audio input type to HDMI."""
        # Arrange
        source = "hdmi"
        tx = "TX-Dante"
        expected_command = "config set device audio input type hdmi TX-Dante"
        expected_response = "config set device audio input type hdmi TX-Dante"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_input_type(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_input_type_analog(self):
        """Test setting device audio input type to analog."""
        # Arrange
        source = "analog"
        tx = "Source1"
        expected_command = "config set device audio input type analog Source1"
        expected_response = "config set device audio input type analog Source1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_input_type(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_dante_audio_input_hdmi(self):
        """Test setting device info Dante audio input to HDMI."""
        # Arrange
        source = "hdmi"
        tx = "TX1"
        expected_command = "config set device info dante.audio_input=hdmi TX1"
        expected_response = "config set device info dante.audio_input=hdmi TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_dante_audio_input(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_dante_audio_input_analog(self):
        """Test setting device info Dante audio input to analog."""
        # Arrange
        source = "analog"
        tx = "TX-Main"
        expected_command = "config set device info dante.audio_input=analog TX-Main"
        expected_response = "config set device info dante.audio_input=analog TX-Main"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_dante_audio_input(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    # =============================================================================
    # 7.3 Port Switching – USB Mode
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_info_km_over_ip_enable_on_tx(self):
        """Test enabling KM over IP on TX device."""
        # Arrange
        enable = "on"
        device = "TX1"
        expected_command = "config set device info km_over_ip_enable=on TX1"
        expected_response = "config set device info km_over_ip_enable=on TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_km_over_ip_enable(enable, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_km_over_ip_enable_off_rx(self):
        """Test disabling KM over IP on RX device."""
        # Arrange
        enable = "off"
        device = "RX1"
        expected_command = "config set device info km_over_ip_enable=off RX1"
        expected_response = "config set device info km_over_ip_enable=off RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_km_over_ip_enable(enable, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_km_over_ip_enable_on_display(self):
        """Test enabling KM over IP on display device."""
        # Arrange
        enable = "on"
        device = "Display1"
        expected_command = "config set device info km_over_ip_enable=on Display1"
        expected_response = "config set device info km_over_ip_enable=on Display1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_km_over_ip_enable(enable, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    # =============================================================================
    # Edge Cases and Command Echo
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_videosource_with_command_echo(self):
        """Test setting device video source with command echo in response."""
        # Arrange
        tx = "TX1"
        source = "hdmi"
        expected_command = "config set device videosource TX1 hdmi"
        expected_response = "config set device videosource TX1 hdmi"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_videosource(tx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audiosource_with_whitespace(self):
        """Test setting device audio source with whitespace in response."""
        # Arrange
        rx = "RX1"
        source = "analog"
        expected_command = "config set device audiosource RX1 analog"
        expected_response = "  config set device audiosource RX1 analog  "
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audiosource(rx, source)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_video_source_switch_with_special_device_name(self):
        """Test setting video source switch with special characters in device name."""
        # Arrange
        source = "usb-c"
        tx = "TX-Wall_Display_1"
        expected_command = "config set device info video_source_switch=usb-c TX-Wall_Display_1"
        expected_response = "config set device info video_source_switch=usb-c TX-Wall_Display_1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_video_source_switch(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio2source_with_multiline_response(self):
        """Test setting device audio2 source with multiline response."""
        # Arrange
        rx = "RX1"
        stream = "dmix"
        expected_command = "config set device audio2source RX1 dmix"
        expected_response = "config set device audio2source RX1 dmix\nAudio2 source configured successfully"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio2source(rx, stream)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_input_type_with_hostname_device(self):
        """Test setting audio input type with hostname-style device name."""
        # Arrange
        source = "analog"
        tx = "NHD-500-DNT-TX-E4CE02104E55"
        expected_command = "config set device audio input type analog NHD-500-DNT-TX-E4CE02104E55"
        expected_response = "config set device audio input type analog NHD-500-DNT-TX-E4CE02104E55"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_input_type(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_dante_audio_input_with_additional_response_text(self):
        """Test setting Dante audio input with additional response text."""
        # Arrange
        source = "hdmi"
        tx = "TX1"
        expected_command = "config set device info dante.audio_input=hdmi TX1"
        expected_response = "config set device info dante.audio_input=hdmi TX1\nDante configuration updated"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_dante_audio_input(source, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_km_over_ip_enable_with_case_sensitivity(self):
        """Test KM over IP setting with case sensitivity considerations."""
        # Arrange
        enable = "off"
        device = "Display_Main"
        expected_command = "config set device info km_over_ip_enable=off Display_Main"
        expected_response = "config set device info km_over_ip_enable=off Display_Main"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_km_over_ip_enable(enable, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
