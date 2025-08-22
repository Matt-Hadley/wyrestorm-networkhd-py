from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.video_stream_text_overlay import VideoStreamTextOverlayCommands


class TestVideoStreamTextOverlayCommands:
    """Unit tests for VideoStreamTextOverlayCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = VideoStreamTextOverlayCommands(self.mock_client)

    # =============================================================================
    # Text Overlay Parameter Configuration
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_osd_param_success(self):
        """Test configuring text overlay parameters."""
        # Arrange
        text = "Test Message"
        position_x = 100
        position_y = 200
        text_color = "FFFF0000"
        text_size = 2
        tx = "TX1"
        expected_command = "config set device osd param Test Message 100 200 FFFF0000 2 TX1"
        expected_response = "config set device osd param Test Message 100 200 FFFF0000 2 TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_osd_param(
            text, position_x, position_y, text_color, text_size, tx
        )

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_osd_param_boundary_values(self):
        """Test configuring text overlay with boundary values."""
        # Arrange
        text = "Boundary Test"
        position_x = 0
        position_y = 1080
        text_color = "FFFFFFFF"
        text_size = 4
        tx = "TX-Main"
        expected_command = "config set device osd param Boundary Test 0 1080 FFFFFFFF 4 TX-Main"
        expected_response = "config set device osd param Boundary Test 0 1080 FFFFFFFF 4 TX-Main"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_osd_param(
            text, position_x, position_y, text_color, text_size, tx
        )

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_osd_param_max_boundaries(self):
        """Test configuring text overlay with maximum boundary values."""
        # Arrange
        text = "Max Position"
        position_x = 1920
        position_y = 0
        text_color = "FF00FFFF"
        text_size = 1
        tx = "TX2"
        expected_command = "config set device osd param Max Position 1920 0 FF00FFFF 1 TX2"
        expected_response = "config set device osd param Max Position 1920 0 FF00FFFF 1 TX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_osd_param(
            text, position_x, position_y, text_color, text_size, tx
        )

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_osd_param_position_x_too_low(self):
        """Test position_x validation with value too low."""
        # Arrange
        text = "Test"
        position_x = -1
        position_y = 100
        text_color = "FFFF0000"
        text_size = 2
        tx = "TX1"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await self.commands.config_set_device_osd_param(text, position_x, position_y, text_color, text_size, tx)

        assert "position_x must be between 0 and 1920" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_device_osd_param_position_x_too_high(self):
        """Test position_x validation with value too high."""
        # Arrange
        text = "Test"
        position_x = 1921
        position_y = 100
        text_color = "FFFF0000"
        text_size = 2
        tx = "TX1"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await self.commands.config_set_device_osd_param(text, position_x, position_y, text_color, text_size, tx)

        assert "position_x must be between 0 and 1920" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_device_osd_param_position_y_too_low(self):
        """Test position_y validation with value too low."""
        # Arrange
        text = "Test"
        position_x = 100
        position_y = -1
        text_color = "FFFF0000"
        text_size = 2
        tx = "TX1"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await self.commands.config_set_device_osd_param(text, position_x, position_y, text_color, text_size, tx)

        assert "position_y must be between 0 and 1080" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_device_osd_param_position_y_too_high(self):
        """Test position_y validation with value too high."""
        # Arrange
        text = "Test"
        position_x = 100
        position_y = 1081
        text_color = "FFFF0000"
        text_size = 2
        tx = "TX1"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await self.commands.config_set_device_osd_param(text, position_x, position_y, text_color, text_size, tx)

        assert "position_y must be between 0 and 1080" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_device_osd_param_text_size_too_low(self):
        """Test text_size validation with value too low."""
        # Arrange
        text = "Test"
        position_x = 100
        position_y = 200
        text_color = "FFFF0000"
        text_size = 0
        tx = "TX1"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await self.commands.config_set_device_osd_param(text, position_x, position_y, text_color, text_size, tx)

        assert "text_size must be between 1 and 4" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_device_osd_param_text_size_too_high(self):
        """Test text_size validation with value too high."""
        # Arrange
        text = "Test"
        position_x = 100
        position_y = 200
        text_color = "FFFF0000"
        text_size = 5
        tx = "TX1"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await self.commands.config_set_device_osd_param(text, position_x, position_y, text_color, text_size, tx)

        assert "text_size must be between 1 and 4" in str(exc_info.value)

    # =============================================================================
    # Text Overlay Enable/Disable
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_device_osd_on(self):
        """Test enabling text overlay."""
        # Arrange
        state = "on"
        tx = "TX1"
        expected_command = "config set device osd on TX1"
        expected_response = "config set device osd on TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_osd(state, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_osd_off(self):
        """Test disabling text overlay."""
        # Arrange
        state = "off"
        tx = "TX-Display"
        expected_command = "config set device osd off TX-Display"
        expected_response = "config set device osd off TX-Display"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_osd(state, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    # =============================================================================
    # Color Hex Utility Methods
    # =============================================================================

    def test_get_color_hex_nhd110_140_red(self):
        """Test getting red color hex for NHD-110/140-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("red", "nhd110_140")
        assert result == "FFFF0000"

    def test_get_color_hex_nhd110_140_white(self):
        """Test getting white color hex for NHD-110/140-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("white", "nhd110_140")
        assert result == "FFFFFFFF"

    def test_get_color_hex_nhd110_140_black(self):
        """Test getting black color hex for NHD-110/140-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("black", "nhd110_140")
        assert result == "FF000000"

    def test_get_color_hex_nhd110_140_purple(self):
        """Test getting purple color hex for NHD-110/140-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("purple", "nhd110_140")
        assert result == "FFFF00FF"

    def test_get_color_hex_nhd110_140_blue(self):
        """Test getting blue color hex for NHD-110/140-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("blue", "nhd110_140")
        assert result == "FF0000FF"

    def test_get_color_hex_nhd110_140_green(self):
        """Test getting green color hex for NHD-110/140-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("green", "nhd110_140")
        assert result == "FF00FFFF"

    def test_get_color_hex_nhd110_140_default(self):
        """Test getting color hex for NHD-110/140-TX with default device type."""
        result = VideoStreamTextOverlayCommands.get_color_hex("red")
        assert result == "FFFF0000"

    def test_get_color_hex_nhd200_red(self):
        """Test getting red color hex for NHD-200-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("red", "nhd200")
        assert result == "FC00"

    def test_get_color_hex_nhd200_white(self):
        """Test getting white color hex for NHD-200-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("white", "nhd200")
        assert result == "FFFF"

    def test_get_color_hex_nhd200_yellow(self):
        """Test getting yellow color hex for NHD-200-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("yellow", "nhd200")
        assert result == "FF00"

    def test_get_color_hex_nhd200_gray(self):
        """Test getting gray color hex for NHD-200-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("gray", "nhd200")
        assert result == "BDEF"

    def test_get_color_hex_nhd200_green(self):
        """Test getting green color hex for NHD-200-TX."""
        result = VideoStreamTextOverlayCommands.get_color_hex("green", "nhd200")
        assert result == "BB00"

    def test_get_color_hex_invalid_color_nhd110_140(self):
        """Test getting invalid color for NHD-110/140-TX raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            VideoStreamTextOverlayCommands.get_color_hex("orange", "nhd110_140")

        assert "Color 'orange' not available for nhd110_140" in str(exc_info.value)
        assert "red, white, black, purple, blue, green" in str(exc_info.value)

    def test_get_color_hex_invalid_color_nhd200(self):
        """Test getting invalid color for NHD-200-TX raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            VideoStreamTextOverlayCommands.get_color_hex("purple", "nhd200")

        assert "Color 'purple' not available for nhd200" in str(exc_info.value)
        assert "red, white, yellow, gray, green" in str(exc_info.value)

    def test_get_color_hex_nhd110_140_unavailable_color(self):
        """Test getting color unavailable for NHD-110/140-TX."""
        with pytest.raises(ValueError) as exc_info:
            VideoStreamTextOverlayCommands.get_color_hex("yellow", "nhd110_140")

        assert "Color 'yellow' not available for nhd110_140" in str(exc_info.value)

    def test_get_color_hex_nhd200_unavailable_color(self):
        """Test getting color unavailable for NHD-200-TX."""
        with pytest.raises(ValueError) as exc_info:
            VideoStreamTextOverlayCommands.get_color_hex("black", "nhd200")

        assert "Color 'black' not available for nhd200" in str(exc_info.value)
