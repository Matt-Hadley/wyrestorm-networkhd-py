"""Convenience wrapper for all command groups.

This module provides the NHDAPI class that organizes all NetworkHD API commands
into logical groups for easy access.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core._client import _BaseNetworkHDClient


class NHDAPI:
    """Typed wrapper for all NHD command groups.

    Provides organized access to all NetworkHD API commands, grouped by functionality.
    Each command group contains related commands for a specific domain.

    This class supports any NetworkHD client implementation, including SSH and RS232 clients.
    Future client implementations are automatically supported.

    Args:
        client: A NetworkHD client instance (NetworkHDClientSSH, NetworkHDClientRS232, etc.)

    Example:
        ```python
        from wyrestorm_networkhd import NetworkHDClientSSH, NHDAPI

        # Create a client
        client = NetworkHDClientSSH(
            host="192.168.1.100",
            port=22,
            username="admin",
            password="password",
            ssh_host_key_policy="auto_add"
        )

        # Create API wrapper
        api = NHDAPI(client)

        # Use command groups
        await api.api_query.get_device_info()
        ```
    """

    def __init__(self, client: "_BaseNetworkHDClient"):
        # Import the base class for runtime validation
        from ..core._client import _BaseNetworkHDClient

        # Validate that the client type is supported
        if not isinstance(client, _BaseNetworkHDClient):
            raise TypeError(
                f"Client must be a NetworkHD client (like NetworkHDClientSSH or NetworkHDClientRS232), "
                f"got {type(client).__name__}"
            )

        # Store the client
        self.client = client

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
