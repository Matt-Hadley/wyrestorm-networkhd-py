from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.multiview import MultiviewCommands
from wyrestorm_networkhd.core.exceptions import CommandError


class TestMultiviewCommands:
    """Unit tests for MultiviewCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = MultiviewCommands(self.mock_client)

    # =============================================================================
    # 11.1 Multiview Decoders – Single Encoder
    # =============================================================================

    @pytest.mark.asyncio
    async def test_mview_set_single_success_without_mode(self):
        """Test setting single TX without mode."""
        # Arrange
        rx = "RX1"
        tx = "TX1"
        expected_command = "mview set RX1 TX1"
        expected_response = "mview set RX1 TX1 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_set_single(rx, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mview_set_single_success_with_tile_mode(self):
        """Test setting single TX with tile mode."""
        # Arrange
        rx = "RX2"
        tx = "TX2"
        mode = "tile"
        expected_command = "mview set RX2 tile TX2"
        expected_response = "mview set RX2 tile TX2 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_set_single(rx, tx, mode)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mview_set_single_success_with_overlay_mode(self):
        """Test setting single TX with overlay mode."""
        # Arrange
        rx = "MultiviewRX"
        tx = "MainTX"
        mode = "overlay"
        expected_command = "mview set MultiviewRX overlay MainTX"
        expected_response = "mview set MultiviewRX overlay MainTX success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_set_single(rx, tx, mode)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mview_set_single_failure(self):
        """Test setting single TX with failure."""
        # Arrange
        rx = "RX1"
        tx = "TX1"
        expected_command = "mview set RX1 TX1"
        expected_response = "mview set RX1 TX1 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mview_set_single(rx, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # 11.2 Multiview Decoders – Preset Tile Layouts
    # =============================================================================

    @pytest.mark.asyncio
    async def test_mscene_active_success(self):
        """Test applying preset multiview layout successfully."""
        # Arrange
        rx = "RX1"
        lname = "Layout1"
        expected_command = "mscene active RX1 Layout1"
        expected_response = "mscene active RX1 Layout1 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_active(rx, lname)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_active_failure(self):
        """Test applying preset multiview layout with failure."""
        # Arrange
        rx = "RX2"
        lname = "BadLayout"
        expected_command = "mscene active RX2 BadLayout"
        expected_response = "mscene active RX2 BadLayout failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mscene_active(rx, lname)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_mscene_change_success(self):
        """Test changing TX for a tile in preset layout."""
        # Arrange
        rx = "MultiRX"
        lname = "QuadLayout"
        tile = 1
        tx = "TX3"
        expected_command = "mscene change MultiRX QuadLayout 1 TX3"
        expected_response = "mscene change MultiRX QuadLayout 1 TX3 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_change(rx, lname, tile, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_change_failure(self):
        """Test changing TX for a tile with failure."""
        # Arrange
        rx = "RX1"
        lname = "Layout1"
        tile = 5  # Invalid tile
        tx = "TX1"
        expected_command = "mscene change RX1 Layout1 5 TX1"
        expected_response = "mscene change RX1 Layout1 5 TX1 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mscene_change(rx, lname, tile, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_mscene_set_audio_window_success(self):
        """Test setting audio to follow tile video."""
        # Arrange
        rx = "AudioRX"
        lname = "AudioLayout"
        tile = 2
        expected_command = "mscene set audio AudioRX AudioLayout window 2"
        expected_response = "mscene set audio AudioRX AudioLayout window 2 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_set_audio(rx, lname, "window", tile)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_set_audio_window_failure(self):
        """Test setting audio window with failure."""
        # Arrange
        rx = "RX1"
        lname = "Layout1"
        tile = 99  # Invalid tile
        expected_command = "mscene set audio RX1 Layout1 window 99"
        expected_response = "mscene set audio RX1 Layout1 window 99 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mscene_set_audio(rx, lname, "window", tile)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_mscene_set_audio_separate_success(self):
        """Test setting separate audio source."""
        # Arrange
        rx = "RX1"
        lname = "Layout1"
        tx = "AudioTX"
        expected_command = "mscene set audio RX1 Layout1 separate AudioTX"
        expected_response = "mscene set audio RX1 Layout1 separate AudioTX success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_set_audio(rx, lname, "separate", tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_set_audio_separate_failure(self):
        """Test setting separate audio source with failure."""
        # Arrange
        rx = "RX1"
        lname = "Layout1"
        tx = "InvalidTX"
        expected_command = "mscene set audio RX1 Layout1 separate InvalidTX"
        expected_response = "mscene set audio RX1 Layout1 separate InvalidTX failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mscene_set_audio(rx, lname, "separate", tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_mscene_set_audio_window_invalid_target_type(self):
        """Test setting audio window with invalid target type (string instead of int)."""
        # Arrange
        rx = "RX1"
        lname = "Layout1"
        invalid_target = "invalid"  # Should be int for window mode

        # Act & Assert
        with pytest.raises(ValueError, match="target must be an integer"):
            await self.commands.mscene_set_audio(rx, lname, "window", invalid_target)

    @pytest.mark.asyncio
    async def test_mscene_set_audio_separate_invalid_target_type(self):
        """Test setting audio separate with invalid target type (int instead of string)."""
        # Arrange
        rx = "RX1"
        lname = "Layout1"
        invalid_target = 123  # Should be string for separate mode

        # Act & Assert
        with pytest.raises(ValueError, match="target must be a string"):
            await self.commands.mscene_set_audio(rx, lname, "separate", invalid_target)

    @pytest.mark.asyncio
    async def test_set_device_info_audio_src_hdmiin1(self):
        """Test setting audio source to HDMI input 1."""
        # Arrange
        input_source = "hdmiin1"
        rx = "MV1"
        expected_command = "config set device info audio_src=hdmiin1 MV1"
        expected_response = "config set device info audio_src=hdmiin1 MV1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_audio_src(input_source, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_audio_src_hdmiin4(self):
        """Test setting audio source to HDMI input 4."""
        # Arrange
        input_source = "hdmiin4"
        rx = "MV2"
        expected_command = "config set device info audio_src=hdmiin4 MV2"
        expected_response = "config set device info audio_src=hdmiin4 MV2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_audio_src(input_source, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_audio_mute_hdmi_mute(self):
        """Test muting HDMI audio."""
        # Arrange
        mute_state = "mute"
        rx = "MV1"
        expected_command = "config set device info audio_mute_hdmi=mute MV1"
        expected_response = "config set device info audio_mute_hdmi=mute MV1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_audio_mute("audio_mute_hdmi", mute_state, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_audio_mute_hdmi_unmute(self):
        """Test unmuting HDMI audio."""
        # Arrange
        mute_state = "unmute"
        rx = "MV2"
        expected_command = "config set device info audio_mute_hdmi=unmute MV2"
        expected_response = "config set device info audio_mute_hdmi=unmute MV2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_audio_mute("audio_mute_hdmi", mute_state, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_audio_mute_av_mute(self):
        """Test muting analog audio output."""
        # Arrange
        mute_state = "mute"
        rx = "MV1"
        expected_command = "config set device info audio_mute_av=mute MV1"
        expected_response = "config set device info audio_mute_av=mute MV1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_audio_mute("audio_mute_av", mute_state, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_device_info_audio_mute_av_unmute(self):
        """Test unmuting analog audio output."""
        # Arrange
        mute_state = "unmute"
        rx = "MV2"
        expected_command = "config set device info audio_mute_av=unmute MV2"
        expected_response = "config set device info audio_mute_av=unmute MV2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_device_info_audio_mute("audio_mute_av", mute_state, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    # =============================================================================
    # 11.3 Multiview Decoders – Custom Tile Layouts
    # =============================================================================

    def test_tile_config_creation(self):
        """Test TileConfig creation and string conversion."""
        # Arrange & Act
        tile = self.commands.TileConfig("TX1", 0, 0, 960, 540, "fit")

        # Assert
        assert tile.tx == "TX1"
        assert tile.x == 0
        assert tile.y == 0
        assert tile.width == 960
        assert tile.height == 540
        assert tile.scaling == "fit"
        assert tile.to_string() == "TX1:0_0_960_540:fit"

    def test_tile_config_default_scaling(self):
        """Test TileConfig with default scaling."""
        # Arrange & Act
        tile = self.commands.TileConfig("TX2", 100, 200, 800, 600)

        # Assert
        assert tile.scaling == "fit"
        assert tile.to_string() == "TX2:100_200_800_600:fit"

    def test_tile_config_stretch_scaling(self):
        """Test TileConfig with stretch scaling."""
        # Arrange & Act
        tile = self.commands.TileConfig("TX3", 500, 300, 400, 300, "stretch")

        # Assert
        assert tile.scaling == "stretch"
        assert tile.to_string() == "TX3:500_300_400_300:stretch"

    @pytest.mark.asyncio
    async def test_mview_set_custom_single_tile_success(self):
        """Test setting custom layout with single tile."""
        # Arrange
        rx = "CustomRX"
        mode = "tile"
        tiles = [self.commands.TileConfig("TX1", 0, 0, 1920, 1080, "fit")]
        expected_command = "mview set CustomRX tile TX1:0_0_1920_1080:fit"
        expected_response = "mview set CustomRX tile TX1:0_0_1920_1080:fit success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_set_custom(rx, mode, tiles)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mview_set_custom_multiple_tiles_success(self):
        """Test setting custom layout with multiple tiles."""
        # Arrange
        rx = "MultiRX"
        mode = "overlay"
        tiles = [
            self.commands.TileConfig("TX1", 0, 0, 960, 540, "fit"),
            self.commands.TileConfig("TX2", 960, 0, 960, 540, "stretch"),
            self.commands.TileConfig("TX3", 0, 540, 960, 540, "fit"),
        ]
        expected_command = (
            "mview set MultiRX overlay TX1:0_0_960_540:fit TX2:960_0_960_540:stretch TX3:0_540_960_540:fit"
        )
        expected_response = expected_command + " success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_set_custom(rx, mode, tiles)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mview_set_custom_failure(self):
        """Test setting custom layout with failure."""
        # Arrange
        rx = "RX1"
        mode = "tile"
        tiles = [self.commands.TileConfig("TX1", 0, 0, 2000, 1200, "fit")]  # Invalid size
        expected_command = "mview set RX1 tile TX1:0_0_2000_1200:fit"
        expected_response = "mview set RX1 tile TX1:0_0_2000_1200:fit failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mview_set_custom(rx, mode, tiles)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_mview_set_audio_custom_success(self):
        """Test setting custom audio source."""
        # Arrange
        rx = "CustomRX"
        tx = "AudioTX"
        expected_command = "mview set audio CustomRX separate AudioTX"
        expected_response = "mview set audio CustomRX separate AudioTX success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_set_audio_custom(rx, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mview_set_audio_custom_failure(self):
        """Test setting custom audio source with failure."""
        # Arrange
        rx = "RX1"
        tx = "InvalidTX"
        expected_command = "mview set audio RX1 separate InvalidTX"
        expected_response = "mview set audio RX1 separate InvalidTX failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mview_set_audio_custom(rx, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # 11.4 Multiview Decoders – PiP position
    # =============================================================================

    @pytest.mark.asyncio
    async def test_mscene_set_pipposition_top_left(self):
        """Test setting PiP position to top left."""
        # Arrange
        rx = "PiPRX"
        position = 0
        expected_command = "mscene set pipposition PiPRX 2-2 0"
        expected_response = "mscene set pipposition PiPRX 2-2 0 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_set_pipposition(rx, position)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_set_pipposition_bottom_left(self):
        """Test setting PiP position to bottom left."""
        # Arrange
        rx = "PiPRX"
        position = 1
        expected_command = "mscene set pipposition PiPRX 2-2 1"
        expected_response = "mscene set pipposition PiPRX 2-2 1 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_set_pipposition(rx, position)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_set_pipposition_top_right(self):
        """Test setting PiP position to top right."""
        # Arrange
        rx = "PiPRX"
        position = 2
        expected_command = "mscene set pipposition PiPRX 2-2 2"
        expected_response = "mscene set pipposition PiPRX 2-2 2 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_set_pipposition(rx, position)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_set_pipposition_bottom_right(self):
        """Test setting PiP position to bottom right."""
        # Arrange
        rx = "PiPRX"
        position = 3
        expected_command = "mscene set pipposition PiPRX 2-2 3"
        expected_response = "mscene set pipposition PiPRX 2-2 3 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_set_pipposition(rx, position)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_set_pipposition_failure(self):
        """Test setting PiP position with failure."""
        # Arrange
        rx = "BadRX"
        position = 0
        expected_command = "mscene set pipposition BadRX 2-2 0"
        expected_response = "mscene set pipposition BadRX 2-2 0 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.mscene_set_pipposition(rx, position)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # Edge Cases and Response Variations
    # =============================================================================

    @pytest.mark.asyncio
    async def test_mview_set_single_with_special_device_names(self):
        """Test single mode with special characters in device names."""
        # Arrange
        rx = "RX-Display_1"
        tx = "TX_Main-Source"
        expected_command = "mview set RX-Display_1 TX_Main-Source"
        expected_response = "mview set RX-Display_1 TX_Main-Source success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mview_set_single(rx, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_mscene_active_with_special_layout_name(self):
        """Test preset layout with special characters in name."""
        # Arrange
        rx = "RX1"
        lname = "Layout_2x2-HD"
        expected_command = "mscene active RX1 Layout_2x2-HD"
        expected_response = "mscene active RX1 Layout_2x2-HD success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.mscene_active(rx, lname)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
