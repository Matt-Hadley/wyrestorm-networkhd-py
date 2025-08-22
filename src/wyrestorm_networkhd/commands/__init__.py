"""Convenience wrapper for all command groups."""

from ..client import NetworkHDClient


class NHDAPI:
    """Typed wrapper for all NHD command groups."""

    def __init__(self, client: NetworkHDClient):
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

        self.reboot_reset = RebootResetCommands(client)
        self.media_stream_matrix_switch = MediaStreamMatrixSwitchCommands(client)
        self.device_port_switch = DevicePortSwitchCommands(client)
        self.connected_device_control = ConnectedDeviceControlCommands(client)
        self.audio_output = AudioOutputCommands(client)
        self.video_wall = VideoWallCommands(client)
        self.multiview = MultiviewCommands(client)
        self.api_notifications = APINotificationsCommands(client)
        self.api_query = APIQueryCommands(client)
        self.video_stream_text_overlay = VideoStreamTextOverlayCommands(client)
        self.api_endpoint = APIEndpointCommands(client)
