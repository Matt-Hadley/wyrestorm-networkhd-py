from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.audio_output import AudioOutputCommands


class TestAudioOutputCommands:
    """Unit tests for AudioOutputCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = AudioOutputCommands(self.mock_client)

    # =============================================================================
    # 9.1 Volume Control – Analog Audio
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_audio_volume_analog_up(self):
        """Test setting analog audio volume up."""
        # Arrange
        level = "up"
        device = "TX1"
        expected_command = "config set device audio volume up analog TX1"
        expected_response = "config set device audio volume up analog TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_volume_analog(level, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_volume_analog_down(self):
        """Test setting analog audio volume down."""
        # Arrange
        level = "down"
        device = "RX2"
        expected_command = "config set device audio volume down analog RX2"
        expected_response = "config set device audio volume down analog RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_volume_analog(level, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_volume_analog_mute(self):
        """Test setting analog audio mute."""
        # Arrange
        level = "mute"
        device = "TX-Main"
        expected_command = "config set device audio volume mute analog TX-Main"
        expected_response = "config set device audio volume mute analog TX-Main"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_volume_analog(level, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_volume_analog_unmute(self):
        """Test setting analog audio unmute."""
        # Arrange
        level = "unmute"
        device = "RX-Display1"
        expected_command = "config set device audio volume unmute analog RX-Display1"
        expected_response = "config set device audio volume unmute analog RX-Display1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_volume_analog(level, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_volume_analog_with_multiline_response(self):
        """Test setting analog audio volume with multiline response."""
        # Arrange
        level = "up"
        device = "TX1"
        expected_command = "config set device audio volume up analog TX1"
        expected_response = "config set device audio volume up analog TX1\nVolume adjusted successfully"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_volume_analog(level, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_audio_volume_analog_with_whitespace_response(self):
        """Test setting analog audio volume with whitespace in response."""
        # Arrange
        level = "mute"
        device = "RX1"
        expected_command = "config set device audio volume mute analog RX1"
        expected_response = "  config set device audio volume mute analog RX1  "
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_audio_volume_analog(level, device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
