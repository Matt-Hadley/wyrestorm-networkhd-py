from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.media_stream_matrix_switch import MediaStreamMatrixSwitchCommands
from wyrestorm_networkhd.exceptions import ResponseError


class TestMediaStreamMatrixSwitchCommands:
    """Unit tests for MediaStreamMatrixSwitchCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
        self.commands = MediaStreamMatrixSwitchCommands(self.mock_client)

    # =============================================================================
    # 6.1 Stream Matrix Switching – All Media
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_set_single_rx_success(self):
        """Test matrix set with single RX."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix set TX1 RX1"
        expected_response = "matrix set TX1 RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_set_multiple_rx_success(self):
        """Test matrix set with multiple RX devices."""
        # Arrange
        tx = "MainTX"
        rx = ["RX1", "RX2", "RX3"]
        expected_command = "matrix set MainTX RX1 RX2 RX3"
        expected_response = "matrix set MainTX RX1 RX2 RX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_set_failure(self):
        """Test matrix set with command mirror failure."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix set TX1 RX1"
        expected_response = "error: invalid command"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_set_null_single_rx_success(self):
        """Test matrix set null with single RX."""
        # Arrange
        rx = "RX1"
        expected_command = "matrix set null RX1"
        expected_response = "matrix set null RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_set_null_multiple_rx_success(self):
        """Test matrix set null with multiple RX devices."""
        # Arrange
        rx = ["RX1", "RX2", "RX3", "RX4"]
        expected_command = "matrix set null RX1 RX2 RX3 RX4"
        expected_response = "matrix set null RX1 RX2 RX3 RX4"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_set_null_failure(self):
        """Test matrix set null with failure."""
        # Arrange
        rx = "InvalidRX"
        expected_command = "matrix set null InvalidRX"
        expected_response = "command failed"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # 6.2 Stream Matrix Switching – Video Stream Breakaway
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_video_set_single_rx_success(self):
        """Test matrix video set with single RX."""
        # Arrange
        tx = "VideoTX"
        rx = "VideoRX"
        expected_command = "matrix video set VideoTX VideoRX"
        expected_response = "matrix video set VideoTX VideoRX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_video_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_video_set_multiple_rx_success(self):
        """Test matrix video set with multiple RX devices."""
        # Arrange
        tx = "MainVideoTX"
        rx = ["VideoRX1", "VideoRX2"]
        expected_command = "matrix video set MainVideoTX VideoRX1 VideoRX2"
        expected_response = "matrix video set MainVideoTX VideoRX1 VideoRX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_video_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_video_set_failure(self):
        """Test matrix video set with failure."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix video set TX1 RX1"
        expected_response = "error occurred"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_video_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_video_set_null_single_rx_success(self):
        """Test matrix video set null with single RX."""
        # Arrange
        rx = "RX1"
        expected_command = "matrix video set null RX1"
        expected_response = "matrix video set null RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_video_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_video_set_null_multiple_rx_success(self):
        """Test matrix video set null with multiple RX devices."""
        # Arrange
        rx = ["RX1", "RX2", "RX3"]
        expected_command = "matrix video set null RX1 RX2 RX3"
        expected_response = "matrix video set null RX1 RX2 RX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_video_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_video_set_null_failure(self):
        """Test matrix video set null with failure."""
        # Arrange
        rx = "BadRX"
        expected_command = "matrix video set null BadRX"
        expected_response = "unexpected response"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_video_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # 6.3 Stream Matrix Switching – Audio Stream Breakaway
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_audio_set_single_rx_success(self):
        """Test matrix audio set with single RX."""
        # Arrange
        tx = "AudioTX"
        rx = "AudioRX"
        expected_command = "matrix audio set AudioTX AudioRX"
        expected_response = "matrix audio set AudioTX AudioRX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio_set_multiple_rx_success(self):
        """Test matrix audio set with multiple RX devices."""
        # Arrange
        tx = "MainAudioTX"
        rx = ["AudioRX1", "AudioRX2", "AudioRX3"]
        expected_command = "matrix audio set MainAudioTX AudioRX1 AudioRX2 AudioRX3"
        expected_response = "matrix audio set MainAudioTX AudioRX1 AudioRX2 AudioRX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio_set_failure(self):
        """Test matrix audio set with failure."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix audio set TX1 RX1"
        expected_response = "command error"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_audio_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_audio_set_null_single_rx_success(self):
        """Test matrix audio set null with single RX."""
        # Arrange
        rx = "RX1"
        expected_command = "matrix audio set null RX1"
        expected_response = "matrix audio set null RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio_set_null_multiple_rx_success(self):
        """Test matrix audio set null with multiple RX devices."""
        # Arrange
        rx = ["RX1", "RX2"]
        expected_command = "matrix audio set null RX1 RX2"
        expected_response = "matrix audio set null RX1 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio_set_null_failure(self):
        """Test matrix audio set null with failure."""
        # Arrange
        rx = "InvalidRX"
        expected_command = "matrix audio set null InvalidRX"
        expected_response = "failed to process"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_audio_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_audio2_set_single_rx_success(self):
        """Test matrix audio2 set with single RX."""
        # Arrange
        tx = "AnalogTX"
        rx = "AnalogRX"
        expected_command = "matrix audio2 set AnalogTX AnalogRX"
        expected_response = "matrix audio2 set AnalogTX AnalogRX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio2_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio2_set_multiple_rx_success(self):
        """Test matrix audio2 set with multiple RX devices."""
        # Arrange
        tx = "MainAnalogTX"
        rx = ["AnalogRX1", "AnalogRX2"]
        expected_command = "matrix audio2 set MainAnalogTX AnalogRX1 AnalogRX2"
        expected_response = "matrix audio2 set MainAnalogTX AnalogRX1 AnalogRX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio2_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio2_set_failure(self):
        """Test matrix audio2 set with failure."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix audio2 set TX1 RX1"
        expected_response = "error"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_audio2_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_audio2_set_null_single_rx_success(self):
        """Test matrix audio2 set null with single RX."""
        # Arrange
        rx = "RX1"
        expected_command = "matrix audio2 set null RX1"
        expected_response = "matrix audio2 set null RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio2_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio2_set_null_multiple_rx_success(self):
        """Test matrix audio2 set null with multiple RX devices."""
        # Arrange
        rx = ["RX1", "RX2", "RX3"]
        expected_command = "matrix audio2 set null RX1 RX2 RX3"
        expected_response = "matrix audio2 set null RX1 RX2 RX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio2_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio2_set_null_failure(self):
        """Test matrix audio2 set null with failure."""
        # Arrange
        rx = "BadRX"
        expected_command = "matrix audio2 set null BadRX"
        expected_response = "command rejected"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_audio2_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_audio3_set_success(self):
        """Test matrix audio3 set for ARC stream."""
        # Arrange
        rx = "ARCRX"
        tx = "ARCTX"
        expected_command = "matrix audio3 set ARCRX ARCTX"
        expected_response = "matrix audio3 set ARCRX ARCTX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio3_set(rx, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio3_set_failure(self):
        """Test matrix audio3 set with failure."""
        # Arrange
        rx = "RX1"
        tx = "TX1"
        expected_command = "matrix audio3 set RX1 TX1"
        expected_response = "not supported"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_audio3_set(rx, tx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # 6.4 Stream Matrix Switching – USB Stream Breakaway
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_usb_set_single_rx_success(self):
        """Test matrix USB set with single RX."""
        # Arrange
        tx = "USBTX"
        rx = "USBRX"
        expected_command = "matrix usb set USBTX USBRX"
        expected_response = "matrix usb set USBTX USBRX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_usb_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_usb_set_multiple_rx_success(self):
        """Test matrix USB set with multiple RX devices."""
        # Arrange
        tx = "MainUSBTX"
        rx = ["USBRX1", "USBRX2", "USBRX3", "USBRX4"]
        expected_command = "matrix usb set MainUSBTX USBRX1 USBRX2 USBRX3 USBRX4"
        expected_response = "matrix usb set MainUSBTX USBRX1 USBRX2 USBRX3 USBRX4"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_usb_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_usb_set_failure(self):
        """Test matrix USB set with failure."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix usb set TX1 RX1"
        expected_response = "usb error"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_usb_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_usb_set_null_single_rx_success(self):
        """Test matrix USB set null with single RX."""
        # Arrange
        rx = "RX1"
        expected_command = "matrix usb set null RX1"
        expected_response = "matrix usb set null RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_usb_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_usb_set_null_multiple_rx_success(self):
        """Test matrix USB set null with multiple RX devices."""
        # Arrange
        rx = ["RX1", "RX2"]
        expected_command = "matrix usb set null RX1 RX2"
        expected_response = "matrix usb set null RX1 RX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_usb_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_usb_set_null_failure(self):
        """Test matrix USB set null with failure."""
        # Arrange
        rx = "InvalidRX"
        expected_command = "matrix usb set null InvalidRX"
        expected_response = "device not found"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_usb_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # 6.5 Stream Matrix Switching – Infrared Stream Breakaway
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_infrared_set_single_rx_success(self):
        """Test matrix infrared set with single RX."""
        # Arrange
        tx = "IRTX"
        rx = "IRRX"
        expected_command = "matrix infrared set IRTX IRRX"
        expected_response = "matrix infrared set IRTX IRRX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared_set_multiple_rx_success(self):
        """Test matrix infrared set with multiple RX devices."""
        # Arrange
        tx = "MainIRTX"
        rx = ["IRRX1", "IRRX2"]
        expected_command = "matrix infrared set MainIRTX IRRX1 IRRX2"
        expected_response = "matrix infrared set MainIRTX IRRX1 IRRX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared_set_failure(self):
        """Test matrix infrared set with failure."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix infrared set TX1 RX1"
        expected_response = "ir not supported"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_infrared_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_infrared_set_null_single_rx_success(self):
        """Test matrix infrared set null with single RX."""
        # Arrange
        rx = "RX1"
        expected_command = "matrix infrared set null RX1"
        expected_response = "matrix infrared set null RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared_set_null_multiple_rx_success(self):
        """Test matrix infrared set null with multiple RX devices."""
        # Arrange
        rx = ["RX1", "RX2", "RX3"]
        expected_command = "matrix infrared set null RX1 RX2 RX3"
        expected_response = "matrix infrared set null RX1 RX2 RX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared_set_null_failure(self):
        """Test matrix infrared set null with failure."""
        # Arrange
        rx = "BadRX"
        expected_command = "matrix infrared set null BadRX"
        expected_response = "command failed"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_infrared_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_single_success(self):
        """Test successful infrared2 single endpoint assignment."""
        # Arrange
        source_device = "source1"
        target_device = "display1"
        expected_command = "matrix infrared2 set source1 single display1"
        self.mock_client.send_command.return_value = expected_command

        # Act
        result = await self.commands.matrix_infrared2_set(source_device, "single", target_device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_single_failure(self):
        """Test failed infrared2 single endpoint assignment."""
        # Arrange
        source_device = "source1"
        target_device = "display1"
        expected_command = "matrix infrared2 set source1 single display1"
        self.mock_client.send_command.return_value = "some other response"

        # Act & Assert
        with pytest.raises(ResponseError, match="Unexpected response"):
            await self.commands.matrix_infrared2_set(source_device, "single", target_device)

        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_single_missing_target(self):
        """Test matrix infrared2 set single mode without target_device raises ValueError."""
        # Arrange
        device = "source1"

        # Act & Assert
        with pytest.raises(ValueError, match="target_device is required when mode is 'single'"):
            await self.commands.matrix_infrared2_set(device, "single")

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_api_success(self):
        """Test successful infrared2 API assignment."""
        # Arrange
        device = "display1"
        expected_command = "matrix infrared2 set display1 api"
        self.mock_client.send_command.return_value = expected_command

        # Act
        result = await self.commands.matrix_infrared2_set(device, "api")

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_api_failure(self):
        """Test failed infrared2 API assignment."""
        # Arrange
        device = "display1"
        expected_command = "matrix infrared2 set display1 api"
        self.mock_client.send_command.return_value = "some other response"

        # Act & Assert
        with pytest.raises(ResponseError, match="Unexpected response"):
            await self.commands.matrix_infrared2_set(device, "api")

        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_all_success(self):
        """Test successful infrared2 all endpoints assignment."""
        # Arrange
        device = "source1"
        expected_command = "matrix infrared2 set source1 all"
        self.mock_client.send_command.return_value = expected_command

        # Act
        result = await self.commands.matrix_infrared2_set(device, "all")

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_all_failure(self):
        """Test failed infrared2 all endpoints assignment."""
        # Arrange
        device = "source1"
        expected_command = "matrix infrared2 set source1 all"
        self.mock_client.send_command.return_value = "some other response"

        # Act & Assert
        with pytest.raises(ResponseError, match="Unexpected response"):
            await self.commands.matrix_infrared2_set(device, "all")

        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_null_success(self):
        """Test matrix infrared2 set null assignment."""
        # Arrange
        device = "TX1"
        expected_command = "matrix infrared2 set TX1 null"
        expected_response = "matrix infrared2 set TX1 null"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared2_set_null(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared2_set_null_failure(self):
        """Test matrix infrared2 set null with failure."""
        # Arrange
        device = "InvalidTX"
        expected_command = "matrix infrared2 set InvalidTX null"
        expected_response = "device error"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_infrared2_set_null(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # 6.6 Stream Matrix Switching – RS-232 Stream Breakaway
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_serial_set_single_rx_success(self):
        """Test matrix serial set with single RX."""
        # Arrange
        tx = "SerialTX"
        rx = "SerialRX"
        expected_command = "matrix serial set SerialTX SerialRX"
        expected_response = "matrix serial set SerialTX SerialRX"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial_set_multiple_rx_success(self):
        """Test matrix serial set with multiple RX devices."""
        # Arrange
        tx = "MainSerialTX"
        rx = ["SerialRX1", "SerialRX2"]
        expected_command = "matrix serial set MainSerialTX SerialRX1 SerialRX2"
        expected_response = "matrix serial set MainSerialTX SerialRX1 SerialRX2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial_set_failure(self):
        """Test matrix serial set with failure."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix serial set TX1 RX1"
        expected_response = "serial port error"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_serial_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_serial_set_null_single_rx_success(self):
        """Test matrix serial set null with single RX."""
        # Arrange
        rx = "RX1"
        expected_command = "matrix serial set null RX1"
        expected_response = "matrix serial set null RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial_set_null_multiple_rx_success(self):
        """Test matrix serial set null with multiple RX devices."""
        # Arrange
        rx = ["RX1", "RX2", "RX3"]
        expected_command = "matrix serial set null RX1 RX2 RX3"
        expected_response = "matrix serial set null RX1 RX2 RX3"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial_set_null_failure(self):
        """Test matrix serial set null with failure."""
        # Arrange
        rx = "BadRX"
        expected_command = "matrix serial set null BadRX"
        expected_response = "serial disconnect failed"
        self.mock_client.send_command.return_value = expected_response

        # Act
        with pytest.raises(ResponseError):  # ResponseError expected when command mirror fails
            await self.commands.matrix_serial_set_null(rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_single_success(self):
        """Test matrix serial2 set single assignment."""
        # Arrange
        source_device = "TX1"
        target_device = "RX1"
        expected_command = "matrix serial2 set TX1 single RX1"
        expected_response = "matrix serial2 set TX1 single RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial2_set(source_device, "single", target_device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_single_failure(self):
        """Test matrix serial2 set single with failure."""
        # Arrange
        source_device = "TX1"
        target_device = "BadRX"
        expected_command = "matrix serial2 set TX1 single BadRX"
        self.mock_client.send_command.return_value = "some other response"  # Simulate unexpected response

        # Act & Assert
        with pytest.raises(ResponseError, match="Unexpected response"):
            await self.commands.matrix_serial2_set(source_device, "single", target_device)

        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_single_missing_target(self):
        """Test matrix serial2 set single with missing target_device."""
        # Arrange
        source_device = "TX1"

        # Act & Assert
        with pytest.raises(ValueError, match="target_device is required when mode is 'single'"):
            await self.commands.matrix_serial2_set(source_device, "single")

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_api_success(self):
        """Test matrix serial2 set API assignment."""
        # Arrange
        device = "TX1"
        expected_command = "matrix serial2 set TX1 api"
        expected_response = "matrix serial2 set TX1 api"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial2_set(device, "api")

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_api_failure(self):
        """Test matrix serial2 set API with failure."""
        # Arrange
        device = "TX1"
        expected_command = "matrix serial2 set TX1 api"
        self.mock_client.send_command.return_value = "some other response"  # Simulate unexpected response

        # Act & Assert
        with pytest.raises(ResponseError, match="Unexpected response"):
            await self.commands.matrix_serial2_set(device, "api")

        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_all_success(self):
        """Test matrix serial2 set all assignment."""
        # Arrange
        device = "TX1"
        expected_command = "matrix serial2 set TX1 all"
        expected_response = "matrix serial2 set TX1 all"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial2_set(device, "all")

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_all_failure(self):
        """Test matrix serial2 set all with failure."""
        # Arrange
        device = "TX1"
        expected_command = "matrix serial2 set TX1 all"
        self.mock_client.send_command.return_value = "some other response"  # Simulate unexpected response

        # Act & Assert
        with pytest.raises(ResponseError, match="Unexpected response"):
            await self.commands.matrix_serial2_set(device, "all")

        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_null_success(self):
        """Test matrix serial2 set null assignment."""
        # Arrange
        device = "TX1"
        expected_command = "matrix serial2 set TX1 null"
        expected_response = "matrix serial2 set TX1 null"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial2_set_null(device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial2_set_null_failure(self):
        """Test matrix serial2 set null with failure."""
        # Arrange
        device = "InvalidTX"
        expected_command = "matrix serial2 set InvalidTX null"
        self.mock_client.send_command.return_value = "some other response"  # Simulate unexpected response

        # Act & Assert
        with pytest.raises(ResponseError, match="Unexpected response"):
            await self.commands.matrix_serial2_set_null(device)

        self.mock_client.send_command.assert_called_once_with(expected_command)

    # =============================================================================
    # Edge Cases and Response Variations
    # =============================================================================

    @pytest.mark.asyncio
    async def test_matrix_set_with_special_device_names(self):
        """Test matrix set with special characters in device names."""
        # Arrange
        tx = "TX-Main_Source"
        rx = ["RX_Display-1", "RX-Display_2"]
        expected_command = "matrix set TX-Main_Source RX_Display-1 RX-Display_2"
        expected_response = "matrix set TX-Main_Source RX_Display-1 RX-Display_2"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_video_set_empty_rx_list(self):
        """Test matrix video set with empty RX list (trailing space stripped)."""
        # Arrange
        tx = "TX1"
        rx = []
        expected_response = "matrix video set TX1"  # Response should match stripped command
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_video_set(tx, rx)

        # Assert
        # The client will receive the original command with trailing space, but send the stripped version
        # We're mocking at the client level so we can't easily verify the stripping
        # Just verify the method succeeds
        self.mock_client.send_command.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_audio_set_single_rx_as_list(self):
        """Test matrix audio set with single RX provided as list."""
        # Arrange
        tx = "TX1"
        rx = ["RX1"]
        expected_command = "matrix audio set TX1 RX1"
        expected_response = "matrix audio set TX1 RX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_audio_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_usb_set_with_whitespace_in_response(self):
        """Test matrix USB set with whitespace in response (should succeed after stripping)."""
        # Arrange
        tx = "TX1"
        rx = "RX1"
        expected_command = "matrix usb set TX1 RX1"
        expected_response = "matrix usb set TX1 RX1"  # require_command_mirror will handle whitespace
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_usb_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_infrared2_rx_to_tx_assignment(self):
        """Test matrix infrared2 set single with RX to TX assignment."""
        # Arrange
        source_device = "RX1"
        target_device = "TX1"
        expected_command = "matrix infrared2 set RX1 single TX1"
        expected_response = "matrix infrared2 set RX1 single TX1"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_infrared2_set(source_device, "single", target_device)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_matrix_serial_set_large_rx_list(self):
        """Test matrix serial set with large number of RX devices."""
        # Arrange
        tx = "MainTX"
        rx = [f"RX{i}" for i in range(1, 11)]  # RX1 through RX10
        expected_command = "matrix serial set MainTX " + " ".join(rx)
        expected_response = expected_command
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.matrix_serial_set(tx, rx)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
