from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.video_wall import VideoWallCommands
from wyrestorm_networkhd.core.exceptions import CommandError


class TestVideoWallCommands:
    """Unit tests for VideoWallCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = VideoWallCommands(self.mock_client)

    # =============================================================================
    # 10.1 Video Wall – 'Standard Video Wall' Scenes
    # =============================================================================

    @pytest.mark.asyncio
    async def test_scene_active_success(self):
        """Test applying a video wall scene successfully."""
        # Arrange
        videowall = "MainWall"
        scene = "Scene1"
        expected_command = "scene active MainWall-Scene1"
        expected_response = "scene MainWall-Scene1 active success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.scene_active(videowall, scene)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_scene_active_failure(self):
        """Test applying a video wall scene with failure."""
        # Arrange
        videowall = "DisplayWall"
        scene = "Layout2"
        expected_command = "scene active DisplayWall-Layout2"
        expected_response = "scene DisplayWall-Layout2 active failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.scene_active(videowall, scene)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_scene_set_success(self):
        """Test changing encoder assignment in a scene."""
        # Arrange
        videowall = "Wall1"
        scene = "Layout1"
        x = 0
        y = 1
        tx = "TX1"
        expected_command = "scene set Wall1-Layout1 0 1 TX1"
        expected_response = "scene Wall1-Layout1's source in [0,1] change to TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.scene_set(videowall, scene, x, y, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_scene_set_failure(self):
        """Test scene set with unexpected response."""
        # Arrange
        videowall = "Wall2"
        scene = "Layout2"
        x = 2
        y = 3
        tx = "TX2"
        expected_command = "scene set Wall2-Layout2 2 3 TX2"
        expected_response = "unexpected response"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.scene_set(videowall, scene, x, y, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is False

    @pytest.mark.asyncio
    async def test_vw_change_success(self):
        """Test changing encoder for a logical screen."""
        # Arrange
        videowall = "MainWall"
        scene = "Scene1"
        lscreen = "Screen1"
        tx = "TX3"
        expected_command = "vw change MainWall-Scene1_Screen1 TX3"
        expected_response = "videowall change MainWall-Scene1_Screen1 tx connect to TX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.vw_change(videowall, scene, lscreen, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_vw_change_failure(self):
        """Test vw change with unexpected response."""
        # Arrange
        videowall = "Wall1"
        scene = "Scene2"
        lscreen = "Screen2"
        tx = "TX4"
        expected_command = "vw change Wall1-Scene2_Screen2 TX4"
        expected_response = "error: invalid screen"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.vw_change(videowall, scene, lscreen, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is False

    # =============================================================================
    # 10.2 Video Wall – 'Video Wall within a Wall' Scenes
    # =============================================================================

    @pytest.mark.asyncio
    async def test_wscene2_active_success(self):
        """Test applying a video wall within a wall scene successfully."""
        # Arrange
        videowall = "MegaWall"
        wscene = "WScene1"
        expected_command = "wscene2 active MegaWall-WScene1"
        expected_response = "wscene2 active MegaWall-WScene1 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_active(videowall, wscene)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_active_failure(self):
        """Test applying a video wall within a wall scene with failure."""
        # Arrange
        videowall = "TestWall"
        wscene = "TestScene"
        expected_command = "wscene2 active TestWall-TestScene"
        expected_response = "wscene2 active TestWall-TestScene failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.wscene2_active(videowall, wscene)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_wscene2_window_open_success(self):
        """Test opening a window in video wall within a wall scene."""
        # Arrange
        videowall = "BigWall"
        wscene = "Scene1"
        wname = "Window1"
        x = 0
        y = 0
        h = 2
        v = 1
        tx = "TX1"
        expected_command = "wscene2 window open BigWall-Scene1 Window1 0 0 2 1 TX1"
        expected_response = "wscene2 window open BigWall-Scene1 Window1 0 0 2 1 TX1 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_open(videowall, wscene, wname, x, y, h, v, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_open_failure(self):
        """Test opening a window with failure."""
        # Arrange
        videowall = "Wall1"
        wscene = "Scene2"
        wname = "Window2"
        x = 1
        y = 1
        h = 1
        v = 2
        tx = "TX2"
        expected_command = "wscene2 window open Wall1-Scene2 Window2 1 1 1 2 TX2"
        expected_response = "wscene2 window open Wall1-Scene2 Window2 1 1 1 2 TX2 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.wscene2_window_open(videowall, wscene, wname, x, y, h, v, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_wscene2_window_close_success(self):
        """Test closing a window in video wall within a wall scene."""
        # Arrange
        videowall = "MegaWall"
        wscene = "Scene1"
        wname = "Window1"
        expected_command = "wscene2 window close MegaWall-Scene1 Window1"
        expected_response = "wscene2 window close MegaWall-Scene1 Window1 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_close(videowall, wscene, wname)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_close_failure(self):
        """Test closing a window with failure."""
        # Arrange
        videowall = "Wall2"
        wscene = "Scene3"
        wname = "Window3"
        expected_command = "wscene2 window close Wall2-Scene3 Window3"
        expected_response = "wscene2 window close Wall2-Scene3 Window3 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.wscene2_window_close(videowall, wscene, wname)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_wscene2_window_change_success(self):
        """Test changing TX for an open window."""
        # Arrange
        videowall = "DisplayWall"
        wscene = "Layout1"
        wname = "MainWindow"
        tx = "TX5"
        expected_command = "wscene2 window change DisplayWall-Layout1 MainWindow TX5"
        expected_response = "wscene2 window change DisplayWall-Layout1 MainWindow TX5 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_change(videowall, wscene, wname, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_change_failure(self):
        """Test changing TX for a window with failure."""
        # Arrange
        videowall = "TestWall"
        wscene = "TestScene"
        wname = "TestWindow"
        tx = "TX6"
        expected_command = "wscene2 window change TestWall-TestScene TestWindow TX6"
        expected_response = "wscene2 window change TestWall-TestScene TestWindow TX6 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.wscene2_window_change(videowall, wscene, wname, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_wscene2_window_adjust_success(self):
        """Test repositioning and resizing an open window."""
        # Arrange
        videowall = "BigWall"
        wscene = "Scene1"
        wname = "FlexWindow"
        x = 2
        y = 1
        h = 3
        v = 2
        expected_command = "wscene2 window adjust BigWall-Scene1 FlexWindow 2 1 3 2"
        expected_response = "wscene2 window adjust BigWall-Scene1 FlexWindow 2 1 3 2 success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_adjust(videowall, wscene, wname, x, y, h, v)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_adjust_failure(self):
        """Test window adjustment with failure."""
        # Arrange
        videowall = "Wall3"
        wscene = "Scene4"
        wname = "Window4"
        x = 0
        y = 0
        h = 4
        v = 4
        expected_command = "wscene2 window adjust Wall3-Scene4 Window4 0 0 4 4"
        expected_response = "wscene2 window adjust Wall3-Scene4 Window4 0 0 4 4 failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.wscene2_window_adjust(videowall, wscene, wname, x, y, h, v)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_wscene2_window_move_up_success(self):
        """Test moving window layer up."""
        # Arrange
        videowall = "LayeredWall"
        wscene = "MultiLayer"
        wname = "TopWindow"
        layer = "up"
        expected_command = "wscene2 window move LayeredWall-MultiLayer TopWindow up"
        expected_response = "wscene2 window move LayeredWall-MultiLayer TopWindow up success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_move(videowall, wscene, wname, layer)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_move_down_success(self):
        """Test moving window layer down."""
        # Arrange
        videowall = "LayeredWall"
        wscene = "MultiLayer"
        wname = "BottomWindow"
        layer = "down"
        expected_command = "wscene2 window move LayeredWall-MultiLayer BottomWindow down"
        expected_response = "wscene2 window move LayeredWall-MultiLayer BottomWindow down success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_move(videowall, wscene, wname, layer)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_move_top_success(self):
        """Test moving window to top layer."""
        # Arrange
        videowall = "Wall1"
        wscene = "Scene1"
        wname = "PriorityWindow"
        layer = "top"
        expected_command = "wscene2 window move Wall1-Scene1 PriorityWindow top"
        expected_response = "wscene2 window move Wall1-Scene1 PriorityWindow top success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_move(videowall, wscene, wname, layer)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_move_bottom_success(self):
        """Test moving window to bottom layer."""
        # Arrange
        videowall = "Wall2"
        wscene = "Scene2"
        wname = "BackgroundWindow"
        layer = "bottom"
        expected_command = "wscene2 window move Wall2-Scene2 BackgroundWindow bottom"
        expected_response = "wscene2 window move Wall2-Scene2 BackgroundWindow bottom success"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.wscene2_window_move(videowall, wscene, wname, layer)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_wscene2_window_move_failure(self):
        """Test window layer move with failure."""
        # Arrange
        videowall = "ErrorWall"
        wscene = "ErrorScene"
        wname = "ErrorWindow"
        layer = "up"
        expected_command = "wscene2 window move ErrorWall-ErrorScene ErrorWindow up"
        expected_response = "wscene2 window move ErrorWall-ErrorScene ErrorWindow up failure"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(CommandError):  # CommandError expected
            await self.commands.wscene2_window_move(videowall, wscene, wname, layer)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # Edge Cases and Response Variations
    # =============================================================================

    @pytest.mark.asyncio
    async def test_scene_set_with_whitespace_in_response(self):
        """Test scene set with whitespace in response."""
        # Arrange
        videowall = "Wall1"
        scene = "Layout1"
        x = 0
        y = 0
        tx = "TX1"
        expected_command = "scene set Wall1-Layout1 0 0 TX1"
        expected_response = "  scene Wall1-Layout1's source in [0,0] change to TX1  "
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.scene_set(videowall, scene, x, y, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_vw_change_with_whitespace_in_response(self):
        """Test vw change with whitespace in response."""
        # Arrange
        videowall = "MainWall"
        scene = "Scene1"
        lscreen = "Screen1"
        tx = "TX1"
        expected_command = "vw change MainWall-Scene1_Screen1 TX1"
        expected_response = "  videowall change MainWall-Scene1_Screen1 tx connect to TX1  "
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.vw_change(videowall, scene, lscreen, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
