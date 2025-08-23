"""Convenience wrapper for all command groups.

This module provides the NHDAPI class that organizes all NetworkHD API commands
into logical groups for easy access.
"""

from ..core.client_ssh import NetworkHDClientSSH


class NHDAPI:
    """Typed wrapper for all NHD command groups.

    Provides organized access to all NetworkHD API commands, grouped by functionality.
    Each command group contains related commands for a specific domain.

    Args:
        client: NetworkHDClientSSH instance for device communication
    """

    def __init__(self, client: NetworkHDClientSSH):
        # Import only when needed to avoid circular imports and reduce startup time
        from .api_endpoint import APIEndpointCommands
        from .api_notifications import APINotificationsCommands
        from .api_query import APIQueryCommands
        from .audio_output import AudioOutputCommands
        from .connected_device_control import ConnectedDeviceControlCommands
        from .device_port_switch import DevicePortSwitchCommands
        from .media_stream_matrix_switch import MediaStreamMatrixSwitchCommands
        from .multiview import MultiviewCommands
        from .reboot_reset import RebootResetCommands
        from .video_stream_text_overlay import VideoStreamTextOverlayCommands
        from .video_wall import VideoWallCommands

        self.client = client

        # Initialize all command groups
        self.api_endpoint = APIEndpointCommands(client)
        self.api_notifications = APINotificationsCommands(client)
        self.api_query = APIQueryCommands(client)
        self.audio_output = AudioOutputCommands(client)
        self.connected_device_control = ConnectedDeviceControlCommands(client)
        self.device_port_switch = DevicePortSwitchCommands(client)
        self.media_stream_matrix_switch = MediaStreamMatrixSwitchCommands(client)
        self.multiview = MultiviewCommands(client)
        self.reboot_reset = RebootResetCommands(client)
        self.video_stream_text_overlay = VideoStreamTextOverlayCommands(client)
        self.video_wall = VideoWallCommands(client)
