from unittest.mock import Mock

import pytest

from wyrestorm_networkhd import NetworkHDClientSSH
from wyrestorm_networkhd.commands import NHDAPI


class TestNHDAPI:
    """Unit tests for NHDAPI wrapper class."""

    def test_nhdapi_initialization_with_client(self):
        """Test NHDAPI initialization with NetworkHDClientSSH."""
        # Arrange
        mock_client = Mock(spec=NetworkHDClientSSH)

        # Act
        api = NHDAPI(mock_client)

        # Assert
        # Verify all command groups are initialized
        assert hasattr(api, "reboot_reset")
        assert hasattr(api, "media_stream_matrix_switch")
        assert hasattr(api, "device_port_switch")
        assert hasattr(api, "connected_device_control")
        assert hasattr(api, "audio_output")
        assert hasattr(api, "video_wall")
        assert hasattr(api, "multiview")
        assert hasattr(api, "api_notifications")
        assert hasattr(api, "api_query")
        assert hasattr(api, "video_stream_text_overlay")
        assert hasattr(api, "api_endpoint")

        # Verify command groups have client assigned
        assert api.reboot_reset.client is mock_client
        assert api.media_stream_matrix_switch.client is mock_client
        assert api.device_port_switch.client is mock_client
        assert api.connected_device_control.client is mock_client
        assert api.audio_output.client is mock_client
        assert api.video_wall.client is mock_client
        assert api.multiview.client is mock_client
        assert api.api_notifications.client is mock_client
        assert api.api_query.client is mock_client
        assert api.video_stream_text_overlay.client is mock_client
        assert api.api_endpoint.client is mock_client

    def test_nhdapi_command_group_types(self):
        """Test that command groups are of correct types."""
        # Arrange
        mock_client = Mock(spec=NetworkHDClientSSH)

        # Act
        api = NHDAPI(mock_client)

        # Assert - Import the command classes to verify types
        from wyrestorm_networkhd.commands.api_endpoint import APIEndpointCommands
        from wyrestorm_networkhd.commands.api_notifications import APINotificationsCommands
        from wyrestorm_networkhd.commands.api_query import APIQueryCommands
        from wyrestorm_networkhd.commands.audio_output import AudioOutputCommands
        from wyrestorm_networkhd.commands.connected_device_control import ConnectedDeviceControlCommands
        from wyrestorm_networkhd.commands.device_port_switch import DevicePortSwitchCommands
        from wyrestorm_networkhd.commands.media_stream_matrix_switch import MediaStreamMatrixSwitchCommands
        from wyrestorm_networkhd.commands.multiview import MultiviewCommands
        from wyrestorm_networkhd.commands.reboot_reset import RebootResetCommands
        from wyrestorm_networkhd.commands.video_stream_text_overlay import VideoStreamTextOverlayCommands
        from wyrestorm_networkhd.commands.video_wall import VideoWallCommands

        assert isinstance(api.reboot_reset, RebootResetCommands)
        assert isinstance(api.media_stream_matrix_switch, MediaStreamMatrixSwitchCommands)
        assert isinstance(api.device_port_switch, DevicePortSwitchCommands)
        assert isinstance(api.connected_device_control, ConnectedDeviceControlCommands)
        assert isinstance(api.audio_output, AudioOutputCommands)
        assert isinstance(api.video_wall, VideoWallCommands)
        assert isinstance(api.multiview, MultiviewCommands)
        assert isinstance(api.api_notifications, APINotificationsCommands)
        assert isinstance(api.api_query, APIQueryCommands)
        assert isinstance(api.video_stream_text_overlay, VideoStreamTextOverlayCommands)
        assert isinstance(api.api_endpoint, APIEndpointCommands)

    def test_nhdapi_multiple_instances_independent(self):
        """Test that multiple NHDAPI instances are independent."""
        # Arrange
        mock_client1 = Mock(spec=NetworkHDClientSSH)
        mock_client2 = Mock(spec=NetworkHDClientSSH)

        # Act
        api1 = NHDAPI(mock_client1)
        api2 = NHDAPI(mock_client2)

        # Assert
        assert api1.reboot_reset.client is mock_client1
        assert api2.reboot_reset.client is mock_client2
        assert api1.reboot_reset is not api2.reboot_reset
        assert api1.media_stream_matrix_switch is not api2.media_stream_matrix_switch

    def test_nhdapi_command_groups_have_methods(self):
        """Test that command groups have expected methods available."""
        # Arrange
        mock_client = Mock(spec=NetworkHDClientSSH)

        # Act
        api = NHDAPI(mock_client)

        # Assert - Check that key methods exist on command groups
        assert hasattr(api.reboot_reset, "set_device_reboot")
        assert hasattr(api.media_stream_matrix_switch, "matrix_set")
        assert hasattr(api.device_port_switch, "config_set_device_audiosource")
        assert hasattr(api.connected_device_control, "config_set_device_sinkpower")
        assert hasattr(api.audio_output, "config_set_device_audio_volume_analog")
        assert hasattr(api.video_wall, "scene_active")
        assert hasattr(api.multiview, "mview_set_single")
        assert hasattr(api.api_notifications, "config_set_device_cec_notify")
        assert hasattr(api.api_query, "config_get_device_info")
        assert hasattr(api.video_stream_text_overlay, "config_set_device_osd_param")
        assert hasattr(api.api_endpoint, "config_set_session_alias")

    def test_nhdapi_rejects_non_client(self):
        """Test NHDAPI raises TypeError for objects that are not NetworkHD clients."""
        # Arrange
        not_a_client = Mock()

        # Act & Assert
        with pytest.raises(TypeError, match="Mock"):
            NHDAPI(not_a_client)


class TestPackageExports:
    """Unit tests for the package's public names."""

    def test_all_names_resolve(self):
        """Test every name in __all__ is importable from the package."""
        # Arrange
        import wyrestorm_networkhd

        # Act & Assert
        for name in wyrestorm_networkhd.__all__:
            assert getattr(wyrestorm_networkhd, name) is not None

    def test_exceptions_exported(self):
        """Test exception classes are exported and ResponseError is still a ValueError."""
        # Arrange
        from wyrestorm_networkhd import NetworkHDError, ResponseError

        # Act & Assert
        assert issubclass(ResponseError, NetworkHDError)
        assert issubclass(ResponseError, ValueError)

    def test_rs232_client_is_lazy(self):
        """Test NetworkHDClientRS232 is importable from the package but kept out of __all__."""
        # Arrange
        import wyrestorm_networkhd
        from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232

        # Act & Assert
        assert wyrestorm_networkhd.NetworkHDClientRS232 is NetworkHDClientRS232
        assert "NetworkHDClientRS232" not in wyrestorm_networkhd.__all__

    def test_unknown_attribute_raises(self):
        """Test unknown package attributes raise AttributeError."""
        # Arrange
        import wyrestorm_networkhd

        # Act & Assert
        with pytest.raises(AttributeError):
            _ = wyrestorm_networkhd.DoesNotExist
